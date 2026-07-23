#!/bin/bash

set -e

cd ~/Projects/JOO

DATE=$(date +%F)

echo "========================================"
echo "JOO COMMAND CENTER"
echo "DATE: $DATE"
echo "========================================"

DATE=$DATE ./Scripts/research_gpt.sh

if [ ! -s Research/$DATE/gpt.md ]; then
    echo "❌ Research failed."
    exit 1
fi

DATE=$DATE ./Scripts/knowledge_gpt.sh

if [ ! -s Knowledge/$DATE/gpt.md ]; then
    echo "❌ Knowledge failed."
    exit 1
fi

DATE=$DATE ./Scripts/cio_gpt.sh

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
