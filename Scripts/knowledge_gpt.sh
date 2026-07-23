#!/bin/bash

source "$HOME/Projects/JOO/Scripts/common.sh"
set -e

cd ~/Projects/JOO

mkdir -p Knowledge/$DATE

RESEARCH_FILE="Research/$DATE/gpt.md"

check_file "$RESEARCH_FILE"

PROMPT_FILE=$(mktemp)

cat > "$PROMPT_FILE" <<EOF
$(cat PromptLibrary/P002_Knowledge.md)

==================================================

Research Report

==================================================

$(cat "$RESEARCH_FILE")
EOF

retry codex exec \
  --skip-git-repo-check \
  --ephemeral \
  -o Knowledge/$DATE/gpt.md \
  < "$PROMPT_FILE"

rm "$PROMPT_FILE"

echo
echo "GPT Knowledge created:"
echo "Knowledge/$DATE/gpt.md"

check_file "Knowledge/$DATE/gpt.md"
success "Knowledge Complete"
