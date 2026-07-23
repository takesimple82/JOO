#!/bin/bash

set -e

cd ~/Projects/JOO

mkdir -p Knowledge

DATE=$(date +%F)

PROMPT_FILE=$(mktemp)

cat > "$PROMPT_FILE" <<EOF
$(cat PromptLibrary/P002_Knowledge.md)

==================================================

Daily Research

==================================================

$(cat Research/$DATE.md)
EOF
grok --prompt-file "$PROMPT_FILE" \
| python3 -c '
import sys

text = sys.stdin.read()

idx = text.find("# Daily Knowledge")

if idx != -1:
    print(text[idx:], end="")
' > "Knowledge/$DATE.md"

rm "$PROMPT_FILE"

echo
echo "Knowledge created:"
echo "Knowledge/$DATE.md"
