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

TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_tool(func: Callable[..., Any]):
    """Register a tool function and return it unchanged."""
    TOOL_REGISTRY[func.__name__] = func
    return func


mcp: Any | None = None



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
        """Return available index fields and example values."""
        idx = load_indexes()

        # Apply maxcount limit
        limited_items = list(idx.items())[:maxcount]

        # build field->set(values)
        fields = {}
        for docid, meta in limited_items:
            for k, v in meta.items():
                fields.setdefault(k, set()).add(str(v))

        return {
            "success": True,
            "count": len(limited_items),
            "fields": {k: sorted(list(v)) for k, v in fields.items()}
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

    @app.get("/api/v1/documents/{doc_id}/json", response_model=dict)
    def get_document_json(doc_id: str):
        """Return document text content as JSON for Salesforce compatibility."""
        pdf_path = ASSETS_DIR / f"{doc_id}"
        if not pdf_path.exists():
            if not pdf_path.suffix:
                pdf_path = ASSETS_DIR / f"{doc_id}.pdf"
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in assets")
        ensure_text_dir()
        text_file = TEXT_DIR / f"{pdf_path.stem}.txt"
        if text_file.exists():
            content = text_file.read_text(encoding='utf-8')
        else:
            content = extract_text_from_pdf(pdf_path)
            try:
                text_file.write_text(content, encoding='utf-8')
            except Exception:
                pass
        return {"doc_id": str(pdf_path.name), "content": content}

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
