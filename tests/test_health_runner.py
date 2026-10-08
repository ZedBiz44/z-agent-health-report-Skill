import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).parents[1] / 'scripts'
spec = importlib.util.spec_from_file_location('runner', SCRIPTS / 'run-openclaw-checks.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class HealthRunnerTests(unittest.TestCase):
    def test_waits_for_exit_and_continues_after_failed_check(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / 'active'
            first = 'import pathlib,time,sys;p=pathlib.Path(sys.argv[1]);p.write_text("active");time.sleep(0.1);p.unlink();sys.exit(3)'
            second = 'import pathlib,sys;sys.exit(9 if pathlib.Path(sys.argv[1]).exists() else 0)'
            saved = []
            commands = [('doctor', [sys.executable, '-c', first, str(marker)]), ('health', [sys.executable, '-c', second, str(marker)])]
            rows = runner.run_checks(commands, os.environ.copy(), lambda r: saved.append(len(r)), sample=lambda: None)
            self.assertEqual([r['exitCode'] for r in rows], [3, 0])
            self.assertEqual(saved, [1, 2])

    def test_memory_guard_does_not_start_heavy_command(self):
        rows = runner.run_checks([('doctor', ['/command-that-must-not-be-started'])], {}, lambda r: None,
                                 sample=lambda: {'currentBytes': 3*1024**3 - 10, 'limitBytes': 3*1024**3})
        self.assertEqual(rows[0]['execution'], 'not_checked')
        self.assertNotIn('exitCode', rows[0])

    def test_stale_database_rejected_even_when_file_exists(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'frank-state'
            scripts = root / 'workspace/skills/z-agent-health-report/scripts'
            scripts.mkdir(parents=True)
            shutil.copy2(SCRIPTS / 'summarize-openclaw-queues.py', scripts)
            stale = root / '.openclaw/state/openclaw.sqlite'
            stale.parent.mkdir(parents=True)
            stale.touch()
            env = dict(os.environ, HOME=str(root), OPENCLAW_STATE_DIR=str(root))
            result = subprocess.run([sys.executable, str(scripts / 'summarize-openclaw-queues.py'), '--db', str(stale)], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('active state database', result.stderr)

    def test_cross_agent_state_is_rejected(self):
        old_here = runner.HERE
        old_env = os.environ.copy()
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d) / 'victor'
                runner.HERE = root / 'workspace/skills/z-agent-health-report/scripts'
                os.environ['OPENCLAW_STATE_DIR'] = str(Path(d) / 'amanda')
                with self.assertRaisesRegex(ValueError, 'disagree'):
                    runner.active_root()
        finally:
            runner.HERE = old_here
            os.environ.clear()
            os.environ.update(old_env)

    def test_custom_home_uses_live_database_and_returns_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'frank-state'
            scripts = root / 'workspace/skills/z-agent-health-report/scripts'
            scripts.mkdir(parents=True)
            shutil.copy2(SCRIPTS / 'summarize-openclaw-queues.py', scripts)
            db = root / 'state/openclaw.sqlite'
            db.parent.mkdir()
            with sqlite3.connect(db) as c:
                for table in ['delivery_queue_entries', 'channel_ingress_events']:
                    c.execute('CREATE TABLE '+table+' (status TEXT,failed_at INTEGER)')
                c.execute("INSERT INTO delivery_queue_entries VALUES ('failed',1000)")
            env = dict(os.environ, HOME=str(root), OPENCLAW_STATE_DIR=str(root))
            p = subprocess.run([sys.executable, str(scripts / 'summarize-openclaw-queues.py'), '--db', str(db), '--now-ms', '100000000'], env=env, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            data = json.loads(p.stdout)
            self.assertEqual(data['outbound']['historicalFailed'], 1)
            self.assertEqual(data['database'], str(db.resolve()))


if __name__ == '__main__':
    unittest.main()
