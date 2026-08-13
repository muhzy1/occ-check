#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/tmp"
if mount | grep -E '\s/tmp\s' | grep -q 'noexec'; then
    TARGET_DIR="/var/tmp"
    if mount | grep -E '\s/var/tmp\s' | grep -q 'noexec'; then
        TARGET_DIR="/root"
    fi
fi

TARGET_BIN="${TARGET_DIR}/occ-check.pyz"
RELEASE_URL="https://github.com/muhzy1/occ-check/releases/latest/download/occ-check.pyz"

echo "Downloading payload to ${TARGET_BIN}..."
curl -fsSL "${RELEASE_URL}" -o "${TARGET_BIN}"
chmod 0755 "${TARGET_BIN}"

if [ -x "${TARGET_BIN}" ] && ! mount | grep -E "\s${TARGET_DIR}\s" | grep -q 'noexec'; then
    EXEC_CMD="${TARGET_BIN}"
else
    EXEC_CMD="python3 ${TARGET_BIN}"
fi

${EXEC_CMD} "$@"
