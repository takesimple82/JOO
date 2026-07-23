#!/bin/bash

set -e

cd ~/Projects/JOO

mkdir -p Reports

DATE=$(date +%F)

PROMPT_FILE=$(mktemp)

cat > "$PROMPT_FILE" <<EOF
You are the CIO of JOO COMMAND CENTER.

Return ONLY valid markdown.

The FIRST line MUST be exactly:

# JOO COMMAND CENTER — CIO Daily Report

Do not output any thinking.
Do not output progress updates.
Do not say you are collecting data.
Do not say you are analyzing.
Do not explain your reasoning.

========================================
JOO Portfolio Database
========================================

$(cat Portfolio/database.md)

========================================
Daily Instructions
========================================

$(cat PromptLibrary/P003_Daily_CIO.md)

========================================
Current Portfolio
========================================

$(cat Portfolio/portfolio.yaml)
EOF

grok --prompt-file "$PROMPT_FILE" \
| sed -n '/^# JOO COMMAND CENTER — CIO Daily Report/,$p' \
> "Reports/$DATE.md"

rm "$PROMPT_FILE"

echo
echo "CIO report created:"
echo "Reports/$DATE.md"
