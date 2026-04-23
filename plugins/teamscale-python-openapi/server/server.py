import base64
import os
import re
import sys

import httpx
from fastmcp import FastMCP
from fastmcp.server.providers.openapi import OpenAPIProvider, RouteMap, MCPType



BASE_URL = os.environ.get("TEAMSCALE_URL")
USER = os.environ.get("TEAMSCALE_USER")
ACCESS_KEY = os.environ.get("TEAMSCALE_ACCESS_KEY")
ENABLE_TOOLS = os.environ.get("ENABLE_TOOLS")

if not all([BASE_URL, USER, ACCESS_KEY]):
    print(
        "Error: TEAMSCALE_URL, TEAMSCALE_USER, and TEAMSCALE_ACCESS_KEY "
        "environment variables must be set.",
        file=sys.stderr,
    )
    sys.exit(1)

TOKEN = base64.b64encode(f"{USER}:{ACCESS_KEY}".encode()).decode()
HEADERS = {"Authorization": "Basic " + TOKEN}

with httpx.Client(verify=False, headers=HEADERS) as openapi_client:
    openapi_spec = openapi_client.get(f"{BASE_URL}/openapi.json?include-internal=false").json()

api_client = httpx.AsyncClient(
    verify=False,
    base_url=BASE_URL,
    headers=HEADERS,
    timeout=60
)

def custom_route_mapper(route, mcp_type: MCPType) -> MCPType | None:
    """Advanced route type mapping."""
   
    if route.method == 'GET' and re.search(r"\{.*\}", route.path):
        return MCPType.RESOURCE_TEMPLATE

    if route.method == 'GET':
        return MCPType.RESOURCE
    
    return MCPType.TOOL if ENABLE_TOOLS else MCPType.EXCLUDE


provider = OpenAPIProvider(
    openapi_spec=openapi_spec,
    client=api_client,
    route_map_fn=custom_route_mapper,
)

anonymous_access_key = ACCESS_KEY[:3] + "***" + ACCESS_KEY[-3:]
mcp = FastMCP(f"Teamscale MCP Server for {BASE_URL} as {USER} with {anonymous_access_key}", providers=[provider])


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
