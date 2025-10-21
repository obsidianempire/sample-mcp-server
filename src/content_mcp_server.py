"""
Content MCP Server - Using FastMCP for simplified implementation

This server uses FastMCP to handle MCP protocol and provides HTTP mode for Salesforce AgentForce integration.

For MCP usage with compatible clients:
python content_mcp_server.py

For Salesforce AgentForce integration (recommended):
PORT=10000 python content_mcp_server.py
"""

import asyncio
import inspect
import json
import os
from typing import Any, Dict, List, Optional

try:
    from fastmcp import FastMCP  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback only used in restricted envs
    from fastapi import FastAPI
    from fastapi import HTTPException as FastMCPHTTPException
    from pydantic import BaseModel as FastMCPBaseModel

    class _ToolCallRequest(FastMCPBaseModel):
        tool: str
        args: Dict[str, Any] | None = None

    class FastMCP:
        """
        Minimal FastMCP-compatible fallback used when the fastmcp package is not available.
        Supports tool registration plus basic /tools endpoints needed for HTTP mode deployments.
        """

        def __init__(self, name: str | None = None, *_, **__):
            self.name = name or "FastMCP-Fallback"
            self._tools: Dict[str, Any] = {}

        def tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func

            return decorator

        def create_app(self) -> FastAPI:
            app = FastAPI(title=self.name)

            @app.get("/tools/list")
            def list_tools():
                return {
                    "success": True,
                    "tools": [
                        {
                            "name": name,
                            "description": inspect.getdoc(func) or "",
                        }
                        for name, func in self._tools.items()
                    ],
                }

            @app.post("/tools/call")
            async def call_tool(request: _ToolCallRequest):
                tool = self._tools.get(request.tool)
                if tool is None:
                    raise FastMCPHTTPException(
                        status_code=404,
                        detail=f"Tool '{request.tool}' is not registered",
                    )

                kwargs = request.args or {}
                result = tool(**kwargs)
                if inspect.isawaitable(result):
                    result = await result

                return {"success": True, "result": result}

            return app

        def run(self, *_, **__):
            raise RuntimeError(
                "The fastmcp package is not installed. HTTP mode is available, but MCP mode "
                "requires installing fastmcp (pip install fastmcp)."
            )

from pydantic import BaseModel
from pydantic import BaseModel

# ---------------- Data model ----------------
class ContentItem(BaseModel):
    id: str
    cls: str
    text: str
    indexes: Dict[str, str]

# Example dataset
DATA = [
    ContentItem(id="si-001", cls="standing_instruction", text="Transfer $500 monthly from Checking ****1234 to Mortgage ****5678.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="ap-042", cls="autopayment", text="$79.99 to Verizon on the 15th monthly from Credit ****4242.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="sl-310", cls="service_link", text="Linked insurance: Homeowners policy ABC-987 with Acme Insurance.", indexes={"status":"active","customer_id":"C123"}),
    ContentItem(id="sl-456", cls="service_link", text="Closed Roth IRA at Delta Funds (transferred out 2024-12-31).", indexes={"status":"closed","customer_id":"C456"}),
    ContentItem(id="ap-260", cls="autopayment", text="$55.00 to GymPro on the 1st monthly from Credit ****7676.", indexes={"status":"active","customer_id":"C789"}),
]

# Initialize FastMCP server
mcp = FastMCP("Banking Content Server")

@mcp.tool()
def search_content(
    classes: List[str],
    filters: Optional[Dict[str, List[str]]] = None,
    limit: Optional[int] = 50
) -> str:
    """Search and filter banking content items by class and attributes.
    
    Args:
        classes: Content classes to search (standing_instruction, autopayment, service_link)
        filters: Key-value filters to apply (e.g., {"status": ["active"], "customer_id": ["C123"]})
        limit: Maximum number of results to return
    
    Returns:
        JSON string with search results
    """
    if filters is None:
        filters = {}
    
    results = []
    for item in DATA:
        # Filter by classes
        if classes and item.cls not in classes:
            continue
        
        # Apply filters
        match = True
        for key, vals in filters.items():
            if key not in item.indexes or item.indexes[key] not in vals:
                match = False
                break
        
        if match:
            results.append(item.model_dump())
        
        if limit and len(results) >= limit:
            break
    
    return json.dumps({
        "success": True,
        "count": len(results),
        "items": results,
        "summary": f"Found {len(results)} items matching criteria"
    }, indent=2)

# Determine desired runtime mode (HTTP/REST or MCP)
_mode_env = os.getenv("MCP_SERVER_MODE")
if _mode_env:
    _runtime_mode = _mode_env.strip().lower()
elif os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    _runtime_mode = "http"
else:
    _runtime_mode = "mcp"

# Check if running in HTTP mode for Salesforce integration
if _runtime_mode in {"http", "rest"}:
    # HTTP mode for cloud deployment
    from fastapi import FastAPI, Header
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    # Get the FastAPI app from FastMCP
    app = mcp.create_app()
    
    # Add CORS for Salesforce integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # More permissive for testing, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    class SearchRequest(BaseModel):
        classes: str
        status: Optional[str] = None
        customer_id: Optional[str] = None
        limit: Optional[int] = 50
    
    @app.get("/health")
    def health():
        return {"status": "ok", "message": "Content MCP Server is running in HTTP mode"}
    
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
                    
                    const classes = document.getElementById('classes').value;
                    const status = document.getElementById('status').value;
                    const customerId = document.getElementById('customer_id').value;
                    
                    const payload = { classes };
                    if (status) payload.status = status;
                    if (customerId) payload.customer_id = customerId;
                    
                    try {
                        const response = await fetch('/api/v1/actions/search_content', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(payload)
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
    
    # Health check for AWS/Salesforce
    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "content-mcp-server",
            "version": "0.1.0",
            "capabilities": ["mcp", "rest-api", "salesforce-integration"]
        }
    
    # OpenAPI schema endpoint for Salesforce External Service registration
    @app.get("/api/v1/actions")
    def get_openapi_schema():
        """Return OpenAPI schema for Salesforce External Service registration."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Content MCP Service",
                "description": "Banking content search service",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "/api/v1",
                    "description": "Production server"
                }
            ],
            "paths": {
                "/actions/search_content": {
                    "post": {
                        "summary": "Search Content Items",
                        "description": "Search and filter banking content items like standing instructions, autopayments, and service links",
                        "operationId": "searchContent",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "classes": {
                                                "type": "string",
                                                "description": "Comma-separated content classes: standing_instruction, autopayment, service_link"
                                            },
                                            "status": {
                                                "type": "string",
                                                "description": "Filter by status: active, closed"
                                            },
                                            "customer_id": {
                                                "type": "string",
                                                "description": "Filter by customer ID (e.g., C123)"
                                            }
                                        },
                                        "required": ["classes"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "result": {
                                                    "type": "object",
                                                    "properties": {
                                                        "items": {"type": "array"},
                                                        "summary": {"type": "string"},
                                                        "metadata": {"type": "object"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    @app.post("/api/v1/actions/search_content")
    async def execute_search_agentforce(request: SearchRequest):
        """Execute search action for Salesforce AgentForce integration."""
        
        # Parse classes parameter
        class_list = [c.strip() for c in request.classes.split(",") if c.strip()]
        
        # Build filters
        filters = {}
        if request.status:
            filters["status"] = [request.status]
        if request.customer_id:
            filters["customer_id"] = [request.customer_id]
        
        # Call the search function
        result_json = search_content(
            classes=class_list,
            filters=filters,
            limit=request.limit
        )
        
        # Parse the JSON result
        result_data = json.loads(result_json)
        
        return {
            "success": True,
            "result": {
                "items": result_data["items"],
                "summary": result_data["summary"],
                "metadata": {
                    "searched_classes": class_list,
                    "applied_filters": filters,
                    "total_results": result_data["count"]
                }
            }
        }

    if __name__ == "__main__":
        port = int(os.getenv("PORT", 10000))
        uvicorn.run(app, host="0.0.0.0", port=port)

else:
    # MCP mode - FastMCP handles this automatically
    if __name__ == "__main__":
        transport = os.getenv("MCP_TRANSPORT", "sse").strip().lower()
        mcp.run(transport=transport, host="0.0.0.0", port=10000)
