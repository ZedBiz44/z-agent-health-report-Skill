#!/usr/bin/env bash
set -euo pipefail

mode="${1:-daily}"
case "$mode" in
  daily) mode_title="Daily" ;;
  weekly) mode_title="Weekly" ;;
  *) echo "Usage: $0 daily|weekly" >&2; exit 2 ;;
esac

guild_id="1491589465175621794"
channel_id="1546640814573101128"
agents=(Amanda Edith Frank Gohzed Grogar Harry Inga Maggie Marsha Rocky Ruby Suzy Terry Victor Vivian Wilma)

export TZ="America/Edmonton"
date_label="$(date +%F)"
start_ms="$(( $(date -d 'today 00:00' +%s) * 1000 ))"
rows_file="$(mktemp)"
trap 'rm -f "$rows_file"' EXIT

for agent in "${agents[@]}"; do
  result="$(openclaw message search \
    --channel discord \
    --guild-id "$guild_id" \
    --channel-id "$channel_id" \
    --query "Agent $agent" \
    --limit 25 \
    --json 2>/dev/null || true)"

  match="$(printf '%s' "$result" | jq -c \
    --arg agent "$agent" \
    --arg mode "$mode_title" \
    --argjson start "$start_ms" '
      [.payload.results.messages[][]?
       | select((.timestampMs // 0) >= $start)
       | select(.content | startswith("# Agent Health Report"))
       | select(.content | contains("**Agent:** " + $agent))
       | select(.content | contains("**Mode:** " + $mode))]
      | sort_by(.timestampMs)
      | last // empty
    ' 2>/dev/null || true)"

  if [[ -z "$match" ]]; then
    printf '%s\tMISSING\t\t\n' "$agent" >> "$rows_file"
    continue
  fi

  status="$(printf '%s' "$match" | jq -r '.content | split("**Overall:** ")[1] | split("\n")[0]' 2>/dev/null || echo UNKNOWN)"
  timestamp="$(printf '%s' "$match" | jq -r '.timestampUtc // .timestamp // ""')"
  finding="$(printf '%s' "$match" | jq -r '.content | gsub("[\\r\\n]+"; " ") | .[0:1400]')"
  printf '%s\t%s\t%s\t%s\n' "$agent" "$status" "$timestamp" "$finding" >> "$rows_file"
done

expected="${#agents[@]}"
received="$(awk -F '\t' '$2 != "MISSING" {n++} END {print n+0}' "$rows_file")"
healthy="$(awk -F '\t' '$2 == "Healthy" {n++} END {print n+0}' "$rows_file")"
warning="$(awk -F '\t' '$2 == "Warning" {n++} END {print n+0}' "$rows_file")"
needs_attention="$(awk -F '\t' '$2 == "Needs Attention" {n++} END {print n+0}' "$rows_file")"
unknown="$(awk -F '\t' '$2 != "MISSING" && $2 != "Healthy" && $2 != "Warning" && $2 != "Needs Attention" {n++} END {print n+0}' "$rows_file")"
missing="$(awk -F '\t' '$2 == "MISSING" {printf "%s%s", sep, $1; sep=", "} END {if (!sep) printf "None"}' "$rows_file")"

printf 'REPORT_COLLECTION mode=%s date=%s timezone=America/Edmonton expected=%s received=%s healthy=%s warning=%s needs_attention=%s unknown=%s\n' \
  "$mode" "$date_label" "$expected" "$received" "$healthy" "$warning" "$needs_attention" "$unknown"
printf 'MISSING: %s\n' "$missing"
printf 'AGENT_ROWS_BEGIN\n'
cat "$rows_file"
printf 'AGENT_ROWS_END\n'
