"""
Content MCP Server - Model Context Protocol Implementation

This is a proper MCP server that communicates via JSON-RPC over stdio.
It provides content search functionality as MCP tools.

Installation:
pip install mcp

Usage:
python content_mcp_server.py

The server will communicate via stdin/stdout using JSON-RPC protocol.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

# ---------------- Data model ----------------
class ContentItem:
    def __init__(self, id: str, cls: str, text: str, indexes: Dict[str, str]):
        self.id = id
        self.cls = cls
        self.text = text
        self.indexes = indexes
    
    def to_dict(self):
        return {
            "id": self.id,
            "cls": self.cls,
            "text": self.text,
            "indexes": self.indexes
        }

# Example dataset
DATA = [
    ContentItem(id="si-001", cls="standing_instruction", text="Transfer $500 monthly from Checking ****1234 to Mortgage ****5678.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="ap-042", cls="autopayment", text="$79.99 to Verizon on the 15th monthly from Credit ****4242.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="sl-310", cls="service_link", text="Linked insurance: Homeowners policy ABC-987 with Acme Insurance.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="sl-456", cls="service_link", text="Closed Roth IRA at Delta Funds (transferred out 2024-12-31).", indexes={"status":"closed","customer_id":"C456"}),
    ContentItem(id="ap-260", cls="autopayment", text="$55.00 to GymPro on the 1st monthly from Credit ****7676.", indexes={"status":"active","customer_id":"C789"}),
]

# ---------------- MCP Server ----------------
app = Server("content-mcp-server")

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_content",
            description="Search and filter content items by class and attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "classes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Content classes to search (standing_instruction, autopayment, service_link)"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Key-value filters to apply",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 50
                    }
                },
                "required": ["classes"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name != "search_content":
        raise ValueError(f"Unknown tool: {name}")
    
    classes = arguments.get("classes", [])
    filters = arguments.get("filters", {})
    limit = arguments.get("limit", 50)
    
    results = []
    for item in DATA:
        if classes and item.cls not in classes:
            continue
        
        match = True
        for key, vals in filters.items():
            if key not in item.indexes or item.indexes[key] not in vals:
                match = False
                break
        
        if match:
            results.append(item)
        
        if limit and len(results) >= limit:
            break
    
    # Format results as JSON string
    result_data = [item.to_dict() for item in results]
    result_text = json.dumps(result_data, indent=2)
    
    return [
        TextContent(
            type="text",
            text=f"Found {len(results)} content items:\n\n{result_text}"
        )
    ]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
