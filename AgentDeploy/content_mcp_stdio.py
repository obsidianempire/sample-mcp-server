"""
Agentforce-facing MCP STDIO wrapper.

This script forwards `content.search` tool invocations to the hosted
REST service running at https://mcp-sample-p525.onrender.com.
"""

import os
from typing import Dict, List, Optional

import aiohttp
from mcp.server import Server

server = Server("content-mcp")
BASE_URL = os.getenv("CONTENT_API_BASE_URL", "https://mcp-sample-p525.onrender.com").rstrip("/")


@server.tool()
async def content_search(
    classes: List[str],
    filters: Optional[Dict[str, List[str]]] = None,
    limit: int = 50,
) -> Dict[str, object]:
    """Forward the search request to the REST endpoint and return its JSON."""
    payload = {
        "classes": classes,
        "filters": filters or {},
        "limit": limit,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/search", json=payload) as response:
            response.raise_for_status()
            data = await response.json()

    return {"content": data}


if __name__ == "__main__":
    server.run()
