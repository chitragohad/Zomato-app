#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/.." || exit 1
exec python run_api.py
