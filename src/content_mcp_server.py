"""
Content MCP Server - Multi-mode deployment

This server provides HTTP endpoints for Salesforce AgentForce integration and can optionally
expose the Model Context Protocol (MCP) when the ``fastmcp`` package is installed.

For MCP usage with compatible clients:
python src/content_mcp_server.py

For Salesforce AgentForce integration (recommended):
MCP_SERVER_MODE=http PORT=10000 python src/content_mcp_server.py
"""

import inspect
import json
import os
from typing import Any, Callable, Dict, List, Optional

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(func: Callable[..., Any]):
    """Register a tool function and return it unchanged."""
    TOOL_REGISTRY[func.__name__] = func
    return func


mcp: Any | None = None


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

# Register tool for both HTTP and MCP usage
@register_tool
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
    _runtime_mode = "http"

# Check if running in HTTP mode for Salesforce integration
if _runtime_mode in {"http", "rest"}:
    # HTTP mode for cloud deployment
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    import uvicorn

    app = FastAPI(title="Banking Content Server")

    class ToolCallRequest(BaseModel):
        tool: str
        args: Dict[str, Any] | None = None

    class SearchRequest(BaseModel):
        classes: str
        status: Optional[str] = None
        customer_id: Optional[str] = None
        limit: Optional[int] = 50

    # Add CORS for Salesforce integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # More permissive for testing, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/tools/list")
    def list_tools():
        """List registered tools for compatibility with MCP-style clients."""
        return {
            "success": True,
            "tools": [
                {"name": name, "description": inspect.getdoc(func) or ""}
                for name, func in TOOL_REGISTRY.items()
            ],
        }

    @app.post("/tools/call")
    async def call_tool(request: ToolCallRequest):
        """Invoke a registered tool."""
        tool = TOOL_REGISTRY.get(request.tool)
        if tool is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{request.tool}' is not registered",
            )

        kwargs = request.args or {}
        result = tool(**kwargs)
        if inspect.isawaitable(result):
            result = await result

        return {"success": True, "result": result}

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

    # ------------------ Document / Index APIs for AgentForce ------------------
    import pathlib
    from fastapi.responses import FileResponse, PlainTextResponse
    try:
        from PyPDF2 import PdfReader
    except Exception:
        PdfReader = None

    ASSETS_DIR = pathlib.Path(__file__).resolve().parents[1] / "assets"
    TEXT_DIR = ASSETS_DIR / "texts"
    INDEX_FILE = ASSETS_DIR / "indexes.json"

    def ensure_text_dir():
        TEXT_DIR.mkdir(parents=True, exist_ok=True)

    def load_indexes():
        if not INDEX_FILE.exists():
            return {}
        try:
            return json.loads(INDEX_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def extract_text_from_pdf(pdf_path: pathlib.Path) -> str:
        """Extract text from a PDF using PyPDF2 (falls back to empty string)."""
        if PdfReader is None:
            return ""

        try:
            reader = PdfReader(str(pdf_path))
            text_parts = []
            for page in reader.pages:
                try:
                    txt = page.extract_text() or ""
                except Exception:
                    txt = ""
                text_parts.append(txt)
            return "\n".join(text_parts)
        except Exception:
            return ""

    @app.get("/api/v1/indexes")
    def get_indexes():
        """Return available index fields and example values. """
        idx = load_indexes()
        # build field->set(values)
        fields = {}
        for docid, meta in idx.items():
            for k, v in meta.items():
                fields.setdefault(k, set()).add(str(v))

        return {
            "success": True,
            "count": len(idx),
            "fields": {k: sorted(list(v)) for k, v in fields.items()}
        }

    class SearchIndexesRequest(BaseModel):
        filters: Dict[str, List[str]]

    @app.post("/api/v1/search")
    def search_indexes(req: SearchIndexesRequest):
        """Search documents by indexes. Request body: {"filters": {"customer": ["XYY"], "invoice_amount": [">5000"]}}"""
        idx = load_indexes()
        matches = []

        # Simple matching: support exact matches and numeric comparisons for invoice_amount/balance
        for docid, meta in idx.items():
            ok = True
            for key, vals in req.filters.items():
                if key not in meta:
                    ok = False
                    break

                # numeric comparison operator support when value starts with > or <
                value = meta.get(key)
                val_str = str(value)

                # allow any of the provided vals to match
                matched_any = False
                for v in vals:
                    if isinstance(value, (int, float)) and (v.startswith('>') or v.startswith('<')):
                        try:
                            cmp_val = float(v[1:])
                            if v[0] == '>' and float(value) > cmp_val:
                                matched_any = True
                                break
                            if v[0] == '<' and float(value) < cmp_val:
                                matched_any = True
                                break
                        except Exception:
                            continue
                    else:
                        # string equality (case-insensitive)
                        if val_str.lower() == str(v).lower():
                            matched_any = True
                            break

                if not matched_any:
                    ok = False
                    break

            if ok:
                matches.append(docid)

        return {"success": True, "count": len(matches), "document_ids": matches}

    @app.get("/api/v1/documents/{doc_id}")
    def get_document(doc_id: str, format: Optional[str] = "text"):
        """Return document content. format=raw (PDF) or text (default).
        If text is requested and not already extracted, the server will extract and cache it under assets/texts/."""
        pdf_path = ASSETS_DIR / f"{doc_id}"
        # allow passing either with or without .pdf
        if not pdf_path.exists():
            if not pdf_path.suffix:
                pdf_path = ASSETS_DIR / f"{doc_id}.pdf"

        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in assets")

        if format == "raw":
            return FileResponse(str(pdf_path), media_type="application/pdf", filename=pdf_path.name)

        # default: text
        ensure_text_dir()
        text_file = TEXT_DIR / f"{pdf_path.stem}.txt"
        if text_file.exists():
            return PlainTextResponse(text_file.read_text(encoding='utf-8'))

        # extract and cache
        extracted = extract_text_from_pdf(pdf_path)
        try:
            text_file.write_text(extracted, encoding='utf-8')
        except Exception:
            pass

        return PlainTextResponse(extracted)

    if __name__ == "__main__":
        port = int(os.getenv("PORT", 10000))
        uvicorn.run(app, host="0.0.0.0", port=port)

else:
    try:
        from fastmcp import FastMCP  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "MCP mode requires the optional 'fastmcp' package. "
            "Install it with 'pip install fastmcp' or switch to HTTP mode by setting MCP_SERVER_MODE=http."
        ) from exc

    mcp = FastMCP("Banking Content Server")
    for func in TOOL_REGISTRY.values():
        mcp.tool()(func)

    if __name__ == "__main__":
        transport = os.getenv("MCP_TRANSPORT", "sse").strip().lower()
        mcp.run(transport=transport, host="0.0.0.0", port=10000)
