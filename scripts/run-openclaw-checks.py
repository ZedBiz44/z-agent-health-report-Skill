#!/usr/bin/env python3
"""Complete one diagnostic process at a time, without an agent-work deadline."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

HERE = Path(__file__).resolve().parent
MIN_HEADROOM = 1024 * 1024 * 1024
PROBE_HEADROOM = 512 * 1024 * 1024


def active_configuration(root):
    config = Path(os.environ.get('OPENCLAW_CONFIG_PATH', root / 'openclaw.json')).expanduser().resolve()
    if config.parent != root.resolve() or not config.is_file():
        raise ValueError('The active configuration does not match this agent state directory')
    return config


def active_root():
    # The installed skill belongs to this state directory. Do not trust HOME,
    # which is itself the state directory on the VPS2 multi-agent installation.
    installed = HERE.parents[3]
    configured = Path(os.environ.get('OPENCLAW_STATE_DIR', installed)).expanduser().resolve()
    if configured != installed.resolve():
        raise ValueError('Skill location and OPENCLAW_STATE_DIR disagree; no checks launched')
    active_configuration(configured)
    if not (configured / 'state/openclaw.sqlite').is_file():
        raise ValueError('The active agent database is missing; no fallback database is allowed')
    return configured


def memory_sample():
    """Read current cgroup-v2 usage; return unavailable instead of inventing it."""
    try:
        relative = next(x.split('::', 1)[1] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::'))
        folder = Path('/sys/fs/cgroup') / relative.lstrip('/')
        if not (folder / 'memory.current').exists():
            folder = Path('/sys/fs/cgroup')
        maximum = (folder / 'memory.max').read_text().strip()
        current = int((folder / 'memory.current').read_text())
        stats = dict(line.split() for line in (folder / 'memory.stat').read_text().splitlines())
        reclaimable = min(current, int(stats.get('inactive_file', 0)))
        return {'currentBytes': current, 'inactiveFileBytes': reclaimable,
                'workingBytes': current - reclaimable,
                'limitBytes': None if maximum == 'max' else int(maximum)}
    except (OSError, ValueError, StopIteration):
        return None


def run_checks(commands, env, persist, sample=memory_sample):
    results = []
    for name, argv in commands:
        before = sample()
        row = {'check': name, 'command': argv, 'startedAtUtc': dt.datetime.now(dt.UTC).isoformat(), 'memoryBefore': before}
        required = PROBE_HEADROOM if name in ('health', 'channels', 'gateway', 'version') else MIN_HEADROOM
        if name != 'queues' and before and before['limitBytes'] is not None and before['limitBytes'] - before.get('workingBytes', before['currentBytes']) < required:
            row.update(execution='not_checked', reason='Insufficient container memory headroom for another OpenClaw CLI process', requiredHeadroomBytes=required)
        else:
            peak = [before['currentBytes'] if before else 0]
            working_peak = [before.get('workingBytes', before['currentBytes']) if before else 0]
            done = threading.Event()

            def observe():
                while not done.wait(0.2):
                    value = sample()
                    if value:
                        peak[0] = max(peak[0], value['currentBytes'])
                        working_peak[0] = max(working_peak[0], value.get('workingBytes', value['currentBytes']))

            monitor = threading.Thread(target=observe, daemon=True)
            monitor.start()
            try:
                # No subprocess timeout. communicate() waits for process exit;
                # yielding a caller tool session does not advance this loop.
                p = subprocess.run(argv, env=env, capture_output=True, text=True)
                row.update(execution='completed', exitCode=p.returncode, stdout=p.stdout, stderr=p.stderr)
            except OSError as error:
                row.update(execution='failed_to_start', reason=str(error))
            finally:
                done.set()
                monitor.join()
            row['sampledPeakMemoryBytes'] = peak[0] or None
            row['sampledPeakWorkingMemoryBytes'] = working_peak[0] or None
        row['finishedAtUtc'] = dt.datetime.now(dt.UTC).isoformat()
        results.append(row)
        persist(results)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['daily', 'weekly'], required=True)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    root = active_root()
    config = active_configuration(root)
    env = dict(os.environ, OPENCLAW_STATE_DIR=str(root), OPENCLAW_CONFIG_PATH=str(config))
    db = root / 'state/openclaw.sqlite'
    if args.validate_only:
        print(json.dumps({'validated': True, 'stateDirectory': str(root), 'database': str(db)}))
        return 0
    # A shared lock excludes another copy of this report, not unrelated work.
    lock = (root / 'state/health-report.lock').open('a')
    os.chmod(lock.name, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({'execution': 'already_running', 'reason': 'Another health runner owns the report lock'}))
        return 2
    deep = ['--deep'] if args.mode == 'weekly' else []
    commands = [
        ('health', ['openclaw', 'health', '--json', '--timeout', '10000']),
        ('channels', ['openclaw', 'channels', 'status', '--probe', '--json', '--timeout', '10000']),
    ]
    if args.mode == 'weekly':
        commands.extend([
            ('doctor', ['openclaw', 'doctor', *deep, '--json']),
            ('security', ['openclaw', 'security', 'audit', *deep, '--json']),
            ('gateway', ['openclaw', 'gateway', 'status', '--deep', '--json', '--timeout', '10000']),
            ('plugins', ['openclaw', 'plugins', 'list', '--json']),
            ('configuration', ['openclaw', 'config', 'validate', '--json']),
            ('version', ['openclaw', '--version']),
        ])
    commands.append(('queues', [sys.executable, str(HERE / 'summarize-openclaw-queues.py'), '--db', str(db), '--since-hours', '168' if args.mode == 'weekly' else '24']))
    destination = root / 'workspace/artifacts/health-checks'
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination, 0o700)
    run_id = str(uuid.uuid4())
    path = destination / (dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ') + '-' + run_id + '.json')
    record = {'schemaVersion': 1, 'runId': run_id, 'mode': args.mode, 'stateDirectory': str(root), 'database': str(db), 'complete': False, 'checks': []}

    def persist(rows):
        record['checks'] = rows
        tmp = path.with_suffix('.tmp')
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(record, f, indent=2)
        tmp.replace(path)

    persist([])
    results = run_checks(commands, env, persist)
    record['complete'] = True
    record['allCommandsCompleted'] = all(r['execution'] == 'completed' and r['exitCode'] == 0 for r in results)
    persist(results)
    print(json.dumps({'artifact': str(path), **record}, indent=2))
    return 0 if record['allCommandsCompleted'] else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(json.dumps({'execution': 'not_checked', 'reason': str(error)}))
        sys.exit(2)
