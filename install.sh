#!/usr/bin/env sh
set -eu
if [ "$(uname -s)" != Linux ]; then
    echo 'This installer supports native Linux only.' >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Install Python 3.12+ and its venv package. See docs/INSTALL.md.' >&2
    exit 1
fi
cd -- "$(dirname -- "$0")"
exec python3 -B setup_bridge.py "$@"
