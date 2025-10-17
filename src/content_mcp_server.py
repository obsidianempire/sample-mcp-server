"""
Content MCP Server - Model Context Protocol Implementation

This is a proper MCP server that communicates via JSON-RPC over stdio.
It provides content search functionality as MCP tools.

Usage:
python content_mcp_server.py

The server will communicate via stdin/stdout using JSON-RPC protocol.
No external dependencies required - uses only Python standard library.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

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
class MCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    def add_tool(self, name: str, description: str, input_schema: dict):
        """Add a tool to the server."""
        self.tools.append({
            "name": name,
            "description": description,
            "inputSchema": input_schema
        })
    
    async def handle_request(self, request: dict) -> dict:
        """Handle incoming JSON-RPC requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": "0.1.0"
                    }
                }
            elif method == "tools/list":
                result = {"tools": self.tools}
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.call_tool(tool_name, arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def call_tool(self, name: str, arguments: dict) -> dict:
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
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Found {len(results)} content items:\n\n{result_text}"
                }
            ]
        }

# Initialize server
server = MCPServer("content-mcp-server")

# Add search tool
server.add_tool(
    name="search_content",
    description="Search and filter content items by class and attributes",
    input_schema={
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

async def main():
    """Run the MCP server."""
    while True:
        try:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            # Write JSON-RPC response to stdout
            print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
