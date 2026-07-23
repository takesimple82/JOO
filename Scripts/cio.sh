#!/bin/bash

set -e

cd ~/Projects/JOO

mkdir -p Reports

DATE=$(date +%F)

PROMPT_FILE=$(mktemp)

cat > "$PROMPT_FILE" <<EOF
$(cat PromptLibrary/P003_CIO.md)

==================================================

Portfolio Database

==================================================

$(cat Portfolio/database.md)

==================================================

Portfolio

==================================================

$(cat Portfolio/portfolio.yaml)

==================================================

Knowledge

==================================================

$(cat Knowledge/$DATE.md)
EOF

grok --prompt-file "$PROMPT_FILE" \
| python3 -c '
import sys

text = sys.stdin.read()

idx = text.find("# CIO Dashboard")

if idx != -1:
    print(text[idx:], end="")
' > "Reports/$DATE.md"
rm "$PROMPT_FILE"

echo
echo "CIO report created:"
echo "Reports/$DATE.md"
