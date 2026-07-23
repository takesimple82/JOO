#!/bin/bash

set -e

cd ~/Projects/JOO

echo
echo "========================================"
echo "STEP 1 : Daily Research"
echo "========================================"

./Scripts/research.sh

echo
echo "========================================"
echo "STEP 2 : Daily Knowledge"
echo "========================================"

./Scripts/knowledge.sh

echo
echo "========================================"
echo "STEP 3 : CIO Dashboard"
echo "========================================"

./Scripts/cio.sh

echo
echo "========================================"
echo "DONE"
echo "========================================"

echo
echo "Research : Research/$(date +%F).md"
echo "Knowledge: Knowledge/$(date +%F).md"
echo "Report   : Reports/$(date +%F).md"
