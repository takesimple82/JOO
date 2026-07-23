#!/bin/bash

set -e

cd ~/Projects/JOO

mkdir -p Research

DATE=$(date +%F)

PROMPT_FILE=$(mktemp)

cat > "$PROMPT_FILE" <<EOF
$(cat PromptLibrary/P001_Research.md)

==================================================

Portfolio Database

==================================================

$(cat Portfolio/database.md)

==================================================

Current Portfolio

==================================================

$(cat Portfolio/portfolio.yaml)
EOF
grok --prompt-file "$PROMPT_FILE" \
| python3 -c '
import sys

text = sys.stdin.read()

idx = text.find("# Daily Research")

if idx != -1:
    print(text[idx:], end="")
' > "Research/$DATE.md"

rm "$PROMPT_FILE"

echo
echo "Research created:"
echo "Research/$DATE.md"
