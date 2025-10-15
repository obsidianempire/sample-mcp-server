# MCP Content PoC

A minimal **Model Context Protocol (MCP)** server exposing a `content.search` tool that lets an Agent (e.g., **Salesforce Agentforce**) fetch text content by **classes** and **index filters**.

It supports two backends:
- **REST-backed** (`RestContentRepository`) that POSTs to your `/search` endpoint.
- **In-memory demo** with realistic seed data (no external dependencies).

Also included: an optional **FastAPI mock** `/search` server so you can demo different results driven by filters.

## Quick Start (VS Code)

1. **Create a venv & install deps**
   ```bash
   cd mcp-content-poc
   python -m venv .venv
   # Activate the venv (Windows PowerShell):
   .venv\Scripts\Activate.ps1
   # macOS/Linux:
   # source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Option A: In-memory only (no REST)**  
   Make sure `CONTENT_API_BASE_URL` is **unset** in `.env`.

   ```bash
   python src/content_mcp_server.py
   ```
   Connect from your MCP-capable client via **stdio** (Agentforce or local MCP client).

3. **Option B: Run the mock REST & then the MCP server**
   Open **two terminals** in VS Code:
   - Terminal A (mock REST):
     ```bash
     uvicorn src.content_mcp_server:build_mock_api(repo) --factory --host 0.0.0.0 --port 8000
     ```
   - Terminal B (MCP, pointing to mock):
     ```bash
     set -a; source .env 2>/dev/null || true; set +a   # (bash/zsh only; on Windows use 'setx' or edit env manually)
     export CONTENT_API_BASE_URL=http://localhost:8000
     export CONTENT_NO_AUTH=true
     python src/content_mcp_server.py
     ```

4. **VS Code debug**  
   Use the provided **Run and Debug** configurations:
   - *Run MCP Server (stdio)* — launches the MCP server.
   - *Run Mock REST (FastAPI)* — launches the mock `/search` API.

## Tool Contract

### `content.search` → returns concatenated text blob
Input JSON:
```json
{
  "classes": ["standing_instruction","autopayment","service_link"],
  "filters": {
    "status": ["active","current"],
    "customer_id": ["C123"]
  },
  "limit": 200,
  "join_with": "\n---\n"
}
```

### `content.search_ids` → returns `id\tclass\tsnippet` per line

## Example scripted tests (Agent → tool args)
- All active for C123:
```json
{"classes":["standing_instruction","autopayment","service_link"],"filters":{"status":["active"],"customer_id":["C123"]}}
```
- Only autopayments for C789:
```json
{"classes":["autopayment"],"filters":{"status":["active"],"customer_id":["C789"]}}
```
- Insurance links for C456 (exclude closed):
```json
{"classes":["service_link"],"filters":{"status":["active"],"customer_id":["C456"],"service_type":["insurance"]}}
```

## Notes
- The MCP server uses **stdio transport** by default.
- For PoC, set `CONTENT_NO_AUTH=true` to send **no** Authorization header.
