#!/bin/bash
source "$HOME/Projects/JOO/Scripts/common.sh"
set -e

cd ~/Projects/JOO


mkdir -p Research/$DATE

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

retry codex exec \
  --skip-git-repo-check \
  --ephemeral \
  -o Research/$DATE/gpt.md \
  < "$PROMPT_FILE"

rm "$PROMPT_FILE"

echo
echo "GPT Research created:"
echo "Research/$DATE/gpt.md"

check_file "Research/$DATE/gpt.md"
success "Research Complete"
