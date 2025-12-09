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

from fastapi.params import Query
from copy import deepcopy
from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(func: Callable[..., Any]):
    """Register a tool function and return it unchanged."""
    TOOL_REGISTRY[func.__name__] = func
    return func


mcp: Any | None = None

class DocumentTextResponse(BaseModel):
    doc_id: str
    content: str  # this is the full document text

class AskMeRequest(BaseModel):
    userQuery: str
    conversation: Optional[str] = ""

class AskMeResponse(BaseModel):
    answer: str
    context: Dict[str, Any]

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


    # Add CORS for Salesforce integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # More permissive for testing, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



    @app.get("/health")
    def health():
        return {"status": "ok", "message": "Content MCP Server is running in HTTP mode"}


    @app.get("/openapi_salesforce.json")
    def openapi_salesforce():
        schema = deepcopy(app.openapi())
        # Force spec version to 3.0.3 for Salesforce
        schema["openapi"] = "3.0.3"

        # Replace empty schemas {} with { "type": "object" }
        def fix_schemas(node):
            if isinstance(node, dict):
                if "schema" in node and node["schema"] == {}:
                    node["schema"] = {"type": "object"}
                for v in node.values():
                    fix_schemas(v)
            elif isinstance(node, list):
                for v in node:
                    fix_schemas(v)

        fix_schemas(schema)
        return schema

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

    # AskMe API endpoint for external service integration
    @app.post("/askme", response_model=AskMeResponse)
    def ask_me(req: AskMeRequest):
        """
        Proxy endpoint that forwards questions to an external Mobius service.
        
        Environment variables required:
        - MOBIUS_SERVER: The Mobius server hostname
        - MOBIUS_PORT: The Mobius server port
        - MOBIUS_USERNAME: Username for Mobius authentication
        - MOBIUS_PASSWORD: Password for Mobius authentication
        - MOBIUS_REPOSITORY_ID: Repository ID for Mobius service
        """
        # Get configuration from environment variables
        mobius_server = os.getenv("MOBIUS_SERVER")
        mobius_port = os.getenv("MOBIUS_PORT")
        mobius_username = os.getenv("MOBIUS_USERNAME")
        mobius_password = os.getenv("MOBIUS_PASSWORD")
        mobius_repo_id = os.getenv("MOBIUS_REPOSITORY_ID")
        
        # Validate required environment variables
        missing_vars = []
        if not mobius_server:
            missing_vars.append("MOBIUS_SERVER")
        if not mobius_port:
            missing_vars.append("MOBIUS_PORT")
        if not mobius_username:
            missing_vars.append("MOBIUS_USERNAME")
        if not mobius_password:
            missing_vars.append("MOBIUS_PASSWORD")
        if not mobius_repo_id:
            missing_vars.append("MOBIUS_REPOSITORY_ID")
        
        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        # Build the Mobius service URL
        mobius_url = f"https://{mobius_server}:{mobius_port}/mobius/rest/conversations"
        
        # Build the request payload
        payload = {
            "userQuery": req.userQuery,
            "documentIDs": [],
            "repositories": [
                {"id": mobius_repo_id}
            ],
            "context": {
                "conversation": req.conversation or ""
            }
        }
        
        # Set up headers
        headers = {
            "Content-Type": "application/vnd.conversation-request.v1+json",
            "Accept": "application/vnd.conversation-response.v1+json"
        }
        
        try:
            # Make the request to Mobius service with basic authentication
            response = requests.post(
                mobius_url,
                json=payload,
                headers=headers,
                auth=HTTPBasicAuth(mobius_username, mobius_password),
                timeout=30
            )
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse the response
            mobius_response = response.json()
            
            # Extract answer and conversation data from the response
            answer = mobius_response.get("answer", "")
            conversation_data = mobius_response.get("context", {}).get("conversation", "")
            
            # Return in the expected format
            return AskMeResponse(
                answer=answer,
                context={
                    "conversation": conversation_data
                }
            )
            
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code=504,
                detail="Mobius service request timed out"
            )
        except requests.exceptions.ConnectionError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to Mobius service: {str(e)}"
            )
        except requests.exceptions.HTTPError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Mobius service returned an error: {str(e)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Invalid response from Mobius service: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with Mobius service: {str(e)}"
            )

    # OpenAPI schema endpoint for Salesforce External Service registration

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
    def get_indexes(maxcount: int = Query(default=9999, ge=1)):
        """Return available index fields"""
        idx = load_indexes()

        # Apply maxcount limit
        limited_items = list(idx.items())[:maxcount]

        # build field->set(values)
        fields = {}
        for key, meta in limited_items:
            for k, v in meta.items():
                fields.setdefault(k, set()).add(str(v))
        return {
            "success": True,
            "count": len(limited_items),
            "fields": sorted(list(fields.keys()))
        }

    from pydantic import BaseModel
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


    @app.get("/api/v1/documents/{doc_id}/json")
    def get_document_json(doc_id: str):
        """
        Original endpoint – keep as-is for other clients.
        Returns both doc_id and content.
        """
        pdf_path = ASSETS_DIR / f"{doc_id}"
        print(f"pdf_path: {pdf_path}")
        if not pdf_path.exists():
            if not pdf_path.suffix:
                pdf_path = ASSETS_DIR / f"{doc_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in assets")

        ensure_text_dir()
        text_file = TEXT_DIR / f"{pdf_path.stem}.txt"
        if text_file.exists():
            content = text_file.read_text(encoding="utf-8")
        else:
            content = extract_text_from_pdf(pdf_path)
            try:
                text_file.write_text(content, encoding="utf-8")
            except Exception:
                pass

        return {"doc_id": str(pdf_path.name), "content": content}



    # 🔹 Salesforce-friendly alias: return just the text as a string
    @app.get("/api/v1/document_text", response_model=str)
    def get_document_text(doc_id: str):
        """
        Alias endpoint for Salesforce External Services.
        Returns ONLY the document text as a string so Agentforce
        can safely use it as tool output.
        """
        pdf_path = ASSETS_DIR / f"{doc_id}"
        if not pdf_path.exists():
            if not pdf_path.suffix:
                pdf_path = ASSETS_DIR / f"{doc_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in assets")

        ensure_text_dir()
        text_file = TEXT_DIR / f"{pdf_path.stem}.txt"
        if text_file.exists():
            content = text_file.read_text(encoding="utf-8")
        else:
            content = extract_text_from_pdf(pdf_path)
            try:
                text_file.write_text(content, encoding="utf-8")
            except Exception:
                pass

        return content  # <-- plain string
    
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
