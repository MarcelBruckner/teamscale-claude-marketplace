#!/bin/bash
set -e

cd "$(dirname "$0")"

npx @hey-api/openapi-ts \
  -i teamscale-openapi.json \
  -o teamscale-rest-api-client \
  -c @hey-api/client-fetch
