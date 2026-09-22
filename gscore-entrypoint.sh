#!/bin/sh
set -eu

uv sync --locked --inexact --python /usr/local/bin/python
uv run --no-sync --python "${UV_PROJECT_ENVIRONMENT}/bin/python" \
    playwright install chromium

exec uv run --no-sync --python "${UV_PROJECT_ENVIRONMENT}/bin/python" "$@"
