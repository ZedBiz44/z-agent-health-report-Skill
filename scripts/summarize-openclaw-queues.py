#!/usr/bin/env python3
"""Summarize current and historical OpenClaw queue failures without payload data."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
from pathlib import Path


def iso_utc(milliseconds: int | None) -> str | None:
    if milliseconds is None:
        return None
    return dt.datetime.fromtimestamp(milliseconds / 1000, dt.UTC).isoformat().replace("+00:00", "Z")


def table_exists(connection: sqlite3.Connection, name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (name,)
    ).fetchone()
    return row is not None


def summarize_table(
    connection: sqlite3.Connection,
    table: str,
    cutoff_ms: int,
) -> dict[str, int | str | None]:
    row = connection.execute(
        f"""
        SELECT
          COUNT(*),
          SUM(CASE WHEN failed_at >= ? THEN 1 ELSE 0 END),
          MIN(failed_at),
          MAX(failed_at)
        FROM {table}
        WHERE status = 'failed'
        """,
        (cutoff_ms,),
    ).fetchone()
    total = int(row[0] or 0)
    current = int(row[1] or 0)
    return {
        "newFailed": current,
        "historicalFailed": total - current,
        "totalFailed": total,
        "oldestFailedAtUtc": iso_utc(row[2]),
        "newestFailedAtUtc": iso_utc(row[3]),
    }


def summarize(db_path: Path, since_hours: int, now_ms: int) -> dict[str, object]:
    cutoff_ms = now_ms - since_hours * 60 * 60 * 1000
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        result: dict[str, object] = {
            "windowHours": since_hours,
            "windowStartUtc": iso_utc(cutoff_ms),
            "checkedAtUtc": iso_utc(now_ms),
        }
        result["outbound"] = (
            summarize_table(connection, "delivery_queue_entries", cutoff_ms)
            if table_exists(connection, "delivery_queue_entries")
            else {"notChecked": "delivery_queue_entries table is unavailable"}
        )
        result["incoming"] = (
            summarize_table(connection, "channel_ingress_events", cutoff_ms)
            if table_exists(connection, "channel_ingress_events")
            else {"notChecked": "channel_ingress_events table is unavailable"}
        )
        return result
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--since-hours", type=int, default=24)
    parser.add_argument("--now-ms", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.since_hours <= 24 * 31:
        parser.error("--since-hours must be between 1 and 744")
    if not args.db.is_file():
        parser.error("--db must name an existing SQLite file")
    now_ms = args.now_ms or int(dt.datetime.now(dt.UTC).timestamp() * 1000)
    print(json.dumps(summarize(args.db, args.since_hours, now_ms), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
