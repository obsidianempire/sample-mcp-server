"""
Content MCP Server (Python) — Render.com Deployment Ready

This version runs a FastAPI-based REST API that mimics an MCP-compatible service.
It exposes:
  • POST /search  — search and filter in-memory content items
  • GET /health   — simple health check for Render

You can deploy this directly to Render as a **Web Service**.

---
# Local Run
pip install -U fastapi uvicorn aiohttp pydantic
python content_mcp_server.py

Then open http://localhost:10000/health to verify.

---
# Render Deployment Steps
1. Push this repo to GitHub.
2. Go to [https://render.com](https://render.com) → **New +** → **Web Service**.
3. Connect to your repo.
4. Set:
   - **Environment:** Python 3.x
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python content_mcp_server.py`
5. Add env vars (optional):
   - `PORT` → `10000` (Render automatically injects its own `$PORT`, this code respects it)
   - `CONTENT_NO_AUTH=true`
6. Deploy → open the Render URL → test `/health` and `/search` endpoints.

---
# Example query to /search
POST /search
{
  "classes": ["standing_instruction","autopayment","service_link"],
  "filters": {"status": ["active"], "customer_id": ["C123"]}
}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os

app = FastAPI(title="Content MCP Server Demo")

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

# ---------------- Request schema ----------------
class SearchBody(BaseModel):
    classes: List[str]
    filters: Dict[str, List[str]] = {}
    limit: Optional[int] = 50

# ---------------- API routes ----------------
@app.get("/health")
def health():
    return {"status": "ok", "message": "Content MCP Server is running"}

@app.post("/search")
def search_content(body: SearchBody):
    results = []
    for item in DATA:
        if body.classes and item.cls not in body.classes:
            continue
        match = True
        for key, vals in body.filters.items():
            if key not in item.indexes or item.indexes[key] not in vals:
                match = False
                break
        if match:
            results.append(item)
        if body.limit and len(results) >= body.limit:
            break
    return results

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
