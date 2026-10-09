#!/usr/bin/env python3
"""Forced SSH command: fixed read-only fleet evidence, no arbitrary shell."""
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import pwd
import sqlite3
import subprocess
import sys

CONFIG = Path('/etc/zedbiz-fleet-diagnostics.json')

def command(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    return {'exitCode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}

def main():
    allowed = json.loads(CONFIG.read_text())
    request = shlex.split(os.environ.get('SSH_ORIGINAL_COMMAND', ''))
    if len(request) != 2 or request[0] != 'inspect' or request[1] not in allowed:
        print('Only inspect <approved-agent> is allowed', file=sys.stderr)
        return 2
    agent = request[1]
    profile = allowed[agent]
    result = {'agent': agent, 'collectedAtUtc': dt.datetime.now(dt.UTC).isoformat(), 'host': os.uname().nodename}
    result['hostMemory'] = Path('/proc/meminfo').read_text()
    result['processMemory'] = command(['ps', '-eo', 'pid,ppid,user,comm,rss,pcpu,etime', '--sort=-rss'])
    if profile.get('container'):
        result['service'] = command(['docker','inspect','--format','{{json .State}}',profile['container']])
        result['resources'] = command(['docker','stats','--no-stream','--format','{{json .}}',profile['container']])
    else:
        prefix = ['systemctl']
        if profile.get('user'):
            uid = pwd.getpwnam(profile['user']).pw_uid
            prefix = ['runuser','-u',profile['user'],'--','env','XDG_RUNTIME_DIR=/run/user/'+str(uid),'systemctl','--user']
        result['service'] = command(prefix+['show',profile['service'],'--property=LoadState,ActiveState,SubState,NRestarts,ExecMainStartTimestamp,MemoryCurrent,MemoryMax,MainPID'])
    root = Path(profile['root']).resolve()
    db = root/'state/openclaw.sqlite'
    if db.is_file() and db.resolve().is_relative_to(root):
        c = sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True)
        c.row_factory = sqlite3.Row
        result['database'] = str(db)
        # Receipts are evidence only; do not load configuration or credentials.
        result['healthJobs'] = [dict(r) for r in c.execute("select job_id,name,state_json from cron_jobs where name like '%health%'")]
        columns = {r[1] for r in c.execute('pragma table_info(cron_run_receipts)')}
        safe = [v for v in ['job_id','status','started_at_ms','finished_at_ms'] if v in columns]
        if safe:
            result['recentRuns'] = [dict(r) for r in c.execute('select '+','.join(safe)+' from cron_run_receipts order by started_at_ms desc limit 40')]
        c.close()
    artifacts = sorted((p for p in (root/'workspace/artifacts/health-checks').glob('*.json') if p.resolve().is_relative_to(root)),reverse=True)
    result['latestHealthArtifacts'] = [{'path':str(p),'result':json.loads(p.read_text())} for p in artifacts[:2]]
    result['limitations'] = ['This route cannot run repairs, read arbitrary files or provide an interactive shell.', 'Artifacts may contain private operational detail; keep them in private evidence storage.']
    print(json.dumps(result))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
