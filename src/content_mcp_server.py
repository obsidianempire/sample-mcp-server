"""
Content MCP Server - Model Context Protocol Implementation

This server supports two modes:
1. MCP mode: JSON-RPC over stdio (default)
2. HTTP mode: REST API for Render deployment (when PORT env var is set)

For MCP usage:
python content_mcp_server.py

For Render deployment:
PORT=10000 python content_mcp_server.py
"""

import asyncio
import json
import sys
import os
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

# Check if running in HTTP mode (AWS/Render deployment)
if os.getenv("PORT") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    # HTTP mode for cloud deployment
    from fastapi import FastAPI, HTTPException, Header
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    
    app = FastAPI(title="Content MCP Server - HTTP Mode")
    
    # Add CORS for Salesforce integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # More permissive for testing, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    class SearchRequest(BaseModel):
        classes: List[str]
        filters: Dict[str, List[str]] = {}
        limit: Optional[int] = 50
    
    @app.get("/health")
    def health():
        return {"status": "ok", "message": "Content MCP Server is running in HTTP mode"}
    
    @app.post("/tools/call")
    async def call_tool_http(request: SearchRequest):
        """HTTP endpoint that mimics MCP tool calling."""
        arguments = request.dict()
        result = await server.call_tool("search_content", arguments)
        return result
    
    @app.get("/tools/list")
    def list_tools_http():
        """HTTP endpoint to list available tools."""
        return {"tools": server.tools}
    
    @app.get("/", response_class=HTMLResponse)
    def test_interface():
        """Simple web interface to test the server."""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Content MCP Server Test</title></head>
        <body>
            <h1>Content MCP Server Test Interface</h1>
            
            <h2>Test Search Tool</h2>
            <form id="searchForm">
                <label>Classes (comma-separated):</label><br>
                <input type="text" id="classes" value="standing_instruction,autopayment,service_link" style="width:400px"><br><br>
                
                <label>Status Filter:</label><br>
                <select id="status">
                    <option value="">All</option>
                    <option value="active">Active</option>
                    <option value="closed">Closed</option>
                </select><br><br>
                
                <label>Customer ID Filter:</label><br>
                <input type="text" id="customer_id" placeholder="e.g., C123"><br><br>
                
                <button type="submit">Search</button>
            </form>
            
            <h3>Result:</h3>
            <pre id="result"></pre>
            
            <script>
                document.getElementById('searchForm').onsubmit = async (e) => {
                    e.preventDefault();
                    
                    const classes = document.getElementById('classes').value.split(',').map(s => s.trim());
                    const filters = {};
                    
                    const status = document.getElementById('status').value;
                    if (status) filters.status = [status];
                    
                    const customerId = document.getElementById('customer_id').value;
                    if (customerId) filters.customer_id = [customerId];
                    
                    try {
                        const response = await fetch('/tools/call', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({classes, filters, limit: 50})
                        });
                        
                        const result = await response.json();
                        document.getElementById('result').textContent = JSON.stringify(result, null, 2);
                    } catch (error) {
                        document.getElementById('result').textContent = 'Error: ' + error.message;
                    }
                };
            </script>
        </body>
        </html>
        """
    
    # Salesforce-compatible REST API
    @app.get("/api/v1/content")
    async def search_content_salesforce(
        classes: str = "standing_instruction,autopayment,service_link",
        status: str = None,
        customer_id: str = None,
        limit: int = 50,
        authorization: str = Header(None, alias="Authorization")
    ):
        """Salesforce-compatible REST endpoint for content search."""
        
        # Simple API key validation (optional for demo)
        # if authorization != "Bearer your-api-key":
        #     raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Parse parameters
        class_list = [c.strip() for c in classes.split(",")]
        filters = {}
        if status:
            filters["status"] = [status]
        if customer_id:
            filters["customer_id"] = [customer_id]
        
        # Call the MCP tool logic
        arguments = {"classes": class_list, "filters": filters, "limit": limit}
        mcp_result = await server.call_tool("search_content", arguments)
        
        # Transform MCP result to Salesforce-friendly format
        content_text = mcp_result["content"][0]["text"]
        # Extract JSON from the text response
        json_start = content_text.find("[\n")
        if json_start != -1:
            json_data = content_text[json_start:]
            items = json.loads(json_data)
        else:
            items = []
        
        return {
            "success": True,
            "count": len(items),
            "data": items,
            "metadata": {
                "classes_searched": class_list,
                "filters_applied": filters,
                "limit": limit
            }
        }
    
    @app.post("/api/v1/content/search")
    async def search_content_salesforce_post(
        request: SearchRequest,
        authorization: str = Header(None, alias="Authorization")
    ):
        """POST version for complex Salesforce queries."""
        
        # Simple API key validation (optional for demo)
        # if authorization != "Bearer your-api-key":
        #     raise HTTPException(status_code=401, detail="Unauthorized")
        
        arguments = request.dict()
        mcp_result = await server.call_tool("search_content", arguments)
        
        # Transform to Salesforce format
        content_text = mcp_result["content"][0]["text"]
        json_start = content_text.find("[\n")
        if json_start != -1:
            json_data = content_text[json_start:]
            items = json.loads(json_data)
        else:
            items = []
        
        return {
            "success": True,
            "count": len(items),
            "data": items
        }
    
    # Health check for AWS/Salesforce
    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "content-mcp-server",
            "version": "0.1.0",
            "capabilities": ["mcp", "rest-api", "salesforce-integration"]
        }
    
    # AgentForce-specific endpoints
    @app.get("/api/v1/actions")
    def list_actions_agentforce():
        """List available actions for AgentForce agents."""
        return {
            "actions": [
                {
                    "name": "search_content",
                    "displayName": "Search Content Items", 
                    "description": "Search and filter banking content items like standing instructions, autopayments, and service links",
                    "parameters": [
                        {
                            "name": "classes",
                            "type": "string",
                            "required": True,
                            "description": "Comma-separated content classes: standing_instruction, autopayment, service_link"
                        },
                        {
                            "name": "status", 
                            "type": "string",
                            "required": False,
                            "description": "Filter by status: active, closed"
                        },
                        {
                            "name": "customer_id",
                            "type": "string", 
                            "required": False,
                            "description": "Filter by customer ID (e.g., C123)"
                        }
                    ],
                    "returnType": "object"
                }
            ]
        }
    
    @app.post("/api/v1/actions/search_content")
    async def execute_search_agentforce(
        classes: str,
        status: str = None,
        customer_id: str = None,
        limit: int = 50
    ):
        """Execute search action for AgentForce agents."""
        
        # Parse and execute search
        class_list = [c.strip() for c in classes.split(",")]
        filters = {}
        if status:
            filters["status"] = [status]
        if customer_id:
            filters["customer_id"] = [customer_id]
        
        arguments = {"classes": class_list, "filters": filters, "limit": limit}
        mcp_result = await server.call_tool("search_content", arguments)
        
        # AgentForce-friendly response format
        content_text = mcp_result["content"][0]["text"]
        json_start = content_text.find("[\n")
        if json_start != -1:
            json_data = content_text[json_start:]
            items = json.loads(json_data)
        else:
            items = []
        
        return {
            "success": True,
            "result": {
                "items": items,
                "summary": f"Found {len(items)} items matching criteria",
                "metadata": {
                    "searched_classes": class_list,
                    "applied_filters": filters,
                    "total_results": len(items)
                }
            },
            "agentContext": {
                "nextSuggestedActions": [
                    "refine_search" if len(items) > 10 else "create_report",
                    "export_results" if len(items) > 0 else "try_different_criteria"
                ]
            }
        }

    if __name__ == "__main__":
        port = int(os.getenv("PORT", 10000))
        uvicorn.run(app, host="0.0.0.0", port=port)

else:
    # MCP mode (stdio)
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
