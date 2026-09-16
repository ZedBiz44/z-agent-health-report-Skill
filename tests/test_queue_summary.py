import sqlite3
import tempfile
import unittest
from pathlib import Path

import importlib.util


SCRIPT = Path(__file__).parents[1] / "scripts" / "summarize-openclaw-queues.py"
SPEC = importlib.util.spec_from_file_location("queue_summary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class QueueSummaryTest(unittest.TestCase):
    def test_separates_current_and_historical_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "openclaw.sqlite"
            connection = sqlite3.connect(db)
            try:
                for table in ("delivery_queue_entries", "channel_ingress_events"):
                    connection.execute(
                        f"CREATE TABLE {table} (status TEXT NOT NULL, failed_at INTEGER)"
                    )
                connection.executemany(
                    "INSERT INTO delivery_queue_entries VALUES ('failed', ?)",
                    [(1_000,), (90_000_000,)],
                )
                connection.execute(
                    "INSERT INTO channel_ingress_events VALUES ('failed', 1000)"
                )
                connection.commit()
            finally:
                connection.close()
            result = MODULE.summarize(db, since_hours=24, now_ms=100_000_000)
            self.assertEqual(result["outbound"]["newFailed"], 1)
            self.assertEqual(result["outbound"]["historicalFailed"], 1)
            self.assertEqual(result["incoming"]["newFailed"], 0)
            self.assertEqual(result["incoming"]["historicalFailed"], 1)


if __name__ == "__main__":
    unittest.main()
