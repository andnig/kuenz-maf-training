#!/usr/bin/env bash
set -euo pipefail
uv sync --frozen
if [[ ! -f .env ]]; then
    (umask 077; cp .env.example .env)
fi
uv run python umgebung_pruefen.py
