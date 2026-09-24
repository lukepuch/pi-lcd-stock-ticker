#!/usr/bin/env bash
# Sync the repo to the Pi and run the ticker on its LCD for a quick test.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

echo "Syncing to ${PI_USER}@${PI_HOST}:${PI_DIR} ..."
rsync -avz \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache/' \
  "$REPO_DIR/" "${PI_USER}@${PI_HOST}:${PI_DIR}/"

echo "Running on the Pi's display (Ctrl+C here stops it)..."
ssh -t "${PI_USER}@${PI_HOST}" "DISPLAY=${PI_DISPLAY} python3 ${PI_DIR}/main.py"
