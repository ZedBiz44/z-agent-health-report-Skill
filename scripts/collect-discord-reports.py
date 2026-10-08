#!/usr/bin/env python3
"""Collect a complete reporting day, including Discord continuation messages."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
from zoneinfo import ZoneInfo

AGENTS = 'Amanda Edith Frank Gohzed Grogar Harry Inga Maggie Marsha Rocky Ruby Suzy Terry Victor Vivian Wilma'.split()
CHANNEL = '1546640814573101128'
SECTIONS = ['Check Results', 'Current Operational Problems', 'Security Actions', 'Maintenance Notices', 'Historical Records', 'Not Applicable', 'Approved Notices', 'What Needs Attention']

def assemble(messages, mode):
    pending, reports = {}, {}
    for msg in sorted(messages, key=lambda m: int(m['id'])):
        author = msg.get('author', {})
        if not author.get('bot'):
            continue
        key = author.get('id')
        body = msg.get('content', '')
        match = re.search(r'^\*\*Agent:\*\*[ \t]*(\w+)(?:[ \t]+\([^\n]*\))?[ \t]*$', body, re.M)
        if '# Agent Health Report' in body:
            pending.pop(key, None)
            if not match or match[1] not in AGENTS or not re.search(r'\*\*Mode:\*\*\s*'+mode.title()+r'\b', body):
                continue
            # Require the agent's named bot. A forwarded/copied report is not evidence.
            expected_bot = 'ruby-zagent' if match[1] == 'Ruby' else match[1].lower()+'-openclaw'
            if expected_bot != author.get('username', '').lower():
                continue
            row = {'agent': match[1], 'messageIds': [], 'text': '', 'collection': 'incomplete', 'status': 'Unknown'}
            pending[key] = row
            reports[match[1]] = row
        row = pending.get(key)
        if row is None:
            continue
        if row['messageIds'] and ('# Agent Health Report' in body or 'Automatic Fleet Notice' in body or 'AGENT HEALTH SUMMARY' in body):
            pending.pop(key, None)
            continue
        row['messageIds'].append(msg['id'])
        row['text'] += ('\n' if row['text'] else '') + body
        if re.search(r'No changes were made\.(?:\s*\(\d+/\d+\))?\s*$', body):
            text = row['text']
            missing = [s for s in SECTIONS if not re.search(r'^##\s+'+re.escape(s)+r'\s*$', text, re.M)]
            status = re.search(r'^\*\*Overall:\*\*\s*(Healthy|Warning|Needs Attention)\s*$', text, re.M)
            row['missingSections'] = missing
            if not missing and status:
                row.update(collection='complete', status=status[1])
            pending.pop(key, None)
    return [reports.get(a, {'agent': a, 'collection': 'missing', 'status': 'Unknown', 'text': '', 'messageIds': []}) for a in AGENTS]

def collect(mode, call=subprocess.run, now=None):
    now = now or dt.datetime.now(ZoneInfo('America/Edmonton'))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()*1000
    messages, seen, before, errors = [], set(), None, []
    while True:
        argv = ['openclaw', 'message', 'read', '--channel', 'discord', '--target', CHANNEL, '--limit', '100', '--json']
        if before:
            argv += ['--before', before]
        try:
            result = call(argv, capture_output=True, text=True)
            if result.returncode:
                raise ValueError('Discord read failed with exit '+str(result.returncode))
            payload = json.loads(result.stdout)['payload']
            if payload.get('ok') is not True or not isinstance(payload.get('messages'), list):
                raise ValueError('Discord returned an unsuccessful or invalid response')
            page = payload['messages']
            if not page:
                break
            fresh = [m for m in page if m['id'] not in seen]
            if not fresh:
                raise ValueError('Discord pagination did not advance')
            seen.update(m['id'] for m in fresh)
            for m in fresh:
                stamp = m.get('timestampMs') or dt.datetime.fromisoformat(m['timestamp']).timestamp()*1000
                if stamp >= start:
                    messages.append(m)
            oldest = min(fresh, key=lambda m: int(m['id']))
            stamp = oldest.get('timestampMs') or dt.datetime.fromisoformat(oldest['timestamp']).timestamp()*1000
            if stamp < start:
                break
            before = oldest['id']
        except (ValueError, KeyError, TypeError, OSError) as error:
            errors.append(str(error))
            break
    rows = assemble(messages, mode)
    if errors:
        for row in rows:
            row['reportedStatus'] = row['status']
            row['status'] = 'Unknown'
            row['collection'] = 'collection_error'
    return {'mode': mode, 'date': now.date().isoformat(), 'timezone': 'America/Edmonton', 'expected': len(AGENTS),
            'complete': sum(r['collection']=='complete' for r in rows), 'errors': errors,
            'counts': {s: sum(r['status']==s for r in rows) for s in ['Healthy', 'Warning', 'Needs Attention', 'Unknown']}, 'agents': rows}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['daily', 'weekly'])
    args = parser.parse_args()
    record = collect(args.mode)
    root = Path(__file__).resolve().parents[4]
    folder = root/'workspace/artifacts/fleet-health'
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(folder, 0o700)
    path = folder/(dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+args.mode+'.json')
    fd = os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(record, f, indent=2)
    print(json.dumps({'artifact': str(path), **record}, indent=2))
    return 1 if record['errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
