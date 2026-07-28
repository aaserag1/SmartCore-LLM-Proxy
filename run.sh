#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_root"

if command -v python3 >/dev/null 2>&1; then
    exec python3 scripts/start_proxy.py "$@"
fi

exec python scripts/start_proxy.py "$@"
