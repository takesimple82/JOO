
#!/bin/bash

source "$HOME/Projects/JOO/Scripts/common.sh"

set -e

cd ~/Projects/JOO

DATE=${DATE:-$(date +%F)}

mkdir -p Reports/$DATE

PROMPT_FILE=$(mktemp)

check_file "Knowledge/$DATE/gpt.md"

cat > "$PROMPT_FILE" <<EOF
$(cat PromptLibrary/P003_Daily_CIO.md)

==================================================

Knowledge Report

==================================================

$(cat Knowledge/$DATE/gpt.md)
EOF

retry codex exec \
  --skip-git-repo-check \
  --ephemeral \
  -o Reports/$DATE/cio.md \
  < "$PROMPT_FILE"

check_file "Reports/$DATE/cio.md"

rm "$PROMPT_FILE"


echo
echo "GPT CIO created:"
echo "Reports/$DATE/cio.md"

success "CIO Complete"
