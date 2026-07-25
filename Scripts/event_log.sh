#!/bin/sh

set -eu

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <stage> <source> <event_type> <summary>" >&2
    exit 1
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
events_file="$script_dir/../data/events.jsonl"

python3 - "$1" "$2" "$3" "$4" "$events_file" <<'PY'
import datetime
import json
import sys

stage, source, event_type, summary, events_file = sys.argv[1:]
event = {
    "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    "stage": stage,
    "source": source,
    "event_type": event_type,
    "summary": summary,
}

with open(events_file, "a", encoding="utf-8") as output:
    output.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
PY
