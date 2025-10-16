Agentforce Deployment Package
=============================

1. Package contents
-------------------
This folder includes everything Salesforce needs to register your REST-hosted MCP service:
- `AgentDeploy/content_mcp_stdio.py` — STDIO wrapper that forwards tool calls to the hosted `/search` endpoint.
- `AgentDeploy/requirements.txt` — minimal dependency list (`mcp`, `aiohttp`).
- `AgentDeploy/register_agent.md` — this runbook for Salesforce admins.

2. Service overview
-------------------
- The REST API lives at `https://mcp-sample-p525.onrender.com`, exposing `/health` and `/search`.
- The payload schema matches the `SearchBody` definition in the original FastAPI project (`classes`, `filters`, `limit`).
- Tool responses are arrays of objects with `id`, `cls`, `text`, and `indexes`.

3. Validate the hosted API
--------------------------
Run these commands from any environment that can reach the service:
```powershell
curl https://mcp-sample-p525.onrender.com/health
curl -X POST https://mcp-sample-p525.onrender.com/search ^
     -H "Content-Type: application/json" ^
     -d "{\"classes\":[\"standing_instruction\"],\"filters\":{\"customer_id\":[\"C123\"],\"status\":[\"active\"]}}"
```
Expect a 200 OK and JSON payload containing the matching records.

4. Install dependencies in Salesforce environment
-------------------------------------------------
Before registering the tool, ensure the runtime where Agentforce launches MCP tools installs the bundled requirements:
```bash
pip install -r AgentDeploy/requirements.txt
```
> If pip access is restricted, install `mcp` and `aiohttp` through your approved package mechanism.

5. Configure the STDIO wrapper
------------------------------
- Command: `python`
- Arguments: `AgentDeploy/content_mcp_stdio.py`
- Working directory: repository root or whichever directory keeps the `AgentDeploy/` folder intact.
- Environment variables:
  - `CONTENT_API_BASE_URL=https://mcp-sample-p525.onrender.com`
  - Add authentication headers if the REST service is later secured (for example, `CONTENT_API_TOKEN`).

6. Register the tool in Salesforce Agentforce
---------------------------------------------
1. Navigate to **Setup ▸ Agentforce ▸ Tools ▸ New Tool**.
2. Choose **Model Context Protocol**.
3. Supply the command and environment values listed above.
4. Use this tool contract (mirrors the hosted API):
   ```json
   {
     "name": "content.search",
     "description": "Fetches curated content records filtered by class and index values.",
     "inputSchema": {
       "type": "object",
       "properties": {
         "classes": {
           "type": "array",
           "items": { "type": "string" },
           "description": "Target content classes (for example, standing_instruction)."
         },
         "filters": {
           "type": "object",
           "description": "Index filters keyed by index name (for example, status or customer_id)."
         },
         "limit": {
           "type": "integer",
           "minimum": 1,
           "maximum": 200,
           "default": 50
         }
       },
       "required": ["classes"]
     }
   }
   ```
5. Save and attach the tool to the desired agent under **Tools & Integrations**.

7. Test the integration
-----------------------
1. Open **Agentforce Studio** and select the agent with the new tool.
2. In the preview console, issue a request such as “Show active autopayments for customer C123.”
3. Confirm the tool call payload resembles:
   ```json
   {
     "classes": ["standing_instruction", "autopayment", "service_link"],
     "filters": { "status": ["active"], "customer_id": ["C123"] },
     "limit": 50
   }
   ```
4. Verify the response echoes the data returned by the Render service.

8. Troubleshooting
------------------
- **No output**: run `python AgentDeploy/content_mcp_stdio.py` locally to check for import errors.
- **HTTP errors**: confirm `CONTENT_API_BASE_URL` points at a live environment and that the service responds to `/health`.
- **Empty results**: ensure the class/filter values match available records (see sample payload above).
