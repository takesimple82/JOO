#!/bin/bash

# ===========================
# JOO COMMAND CENTER
# Common Library
# Version 2.0
# ===========================

DATE=${DATE:-$(date +%F)}

ROOT="$HOME/Projects/JOO"

LOG_DIR="$ROOT/Logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/$DATE.log"

timestamp() {
    date +"%H:%M:%S"
}

log() {
    echo "[$(timestamp)] $1"
    echo "[$(timestamp)] $1" >> "$LOG_FILE"
}

success() {
    log "SUCCESS : $1"
}

fail() {
    log "FAILED  : $1"
    exit 1
}

check_file() {

    local FILE="$1"

    if [ ! -f "$FILE" ]; then
        fail "Missing file : $FILE"
    fi

    if [ ! -s "$FILE" ]; then
        fail "Empty file : $FILE"
    fi
}
retry() {

    local max=3
    local delay=10
    local attempt=1

    while true; do

        "$@" && return 0

        if [ "$attempt" -ge "$max" ]; then
            fail "Retry failed after ${max} attempts."
        fi

        log "Attempt ${attempt}/${max} failed. Retrying in ${delay}s..."

        sleep "$delay"

        delay=$((delay * 2))
        attempt=$((attempt + 1))

    done
}
