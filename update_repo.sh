#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR" || exit 1

if ping -q -c 1 -W 2 github.com >/dev/null 2>&1; then
    git fetch origin main >/dev/null 2>&1
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    if [ "$LOCAL" != "$REMOTE" ]; then
        git pull origin main >/dev/null 2>&1
        sudo systemctl restart pathly.service
    fi
fi