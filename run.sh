#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
SCRIPTS_DIR=$(awk '
/^scripts:/ {f=1; next}
f && /directory:/ {print $2; exit}
' config.yaml)

echo "Scripts Directory: $SCRIPTS_DIR"

DATE=$(date +%F)
echo

echo "========================================"
echo "JOO COMMAND CENTER"
echo "DATE: $DATE"
echo "========================================"

DATE=$DATE ./$SCRIPTS_DIR/research_gpt.sh

if [ ! -s Research/$DATE/gpt.md ]; then
    echo "❌ Research failed."
    exit 1
fi

DATE=$DATE ./$SCRIPTS_DIR/knowledge_gpt.sh

if [ ! -s Knowledge/$DATE/gpt.md ]; then
    echo "❌ Knowledge failed."
    exit 1
fi

DATE=$DATE ./$SCRIPTS_DIR/cio_gpt.sh

if [ ! -s Reports/$DATE/cio.md ]; then
    echo "❌ CIO failed."
    exit 1
fi

echo
echo "========================================"
echo "✅ Research Complete"
echo "✅ Knowledge Complete"
echo "✅ CIO Complete"
echo
echo "🎉 JOO COMMAND CENTER DONE"
echo "========================================"
