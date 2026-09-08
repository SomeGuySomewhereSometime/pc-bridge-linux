#!/usr/bin/env sh
set -eu
if [ "$(uname -s)" != Linux ]; then
    echo 'Este instalador suporta apenas Linux nativo.' >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Instale Python 3.12+ e o pacote venv. Consulte docs/INSTALL.md.' >&2
    exit 1
fi
cd -- "$(dirname -- "$0")"
exec python3 -B setup_bridge.py "$@"
