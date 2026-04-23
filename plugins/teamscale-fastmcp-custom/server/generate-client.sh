#!/bin/bash
set -e

cd "$(dirname "$0")"

uv run --no-project --with openapi-python-client openapi-python-client generate --path teamscale-openapi.json --overwrite
uv sync
