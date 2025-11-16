


# Agentforce Deployment Package

---

## 1. Package Contents

This folder includes everything Salesforce needs to register your REST-hosted MCP service:
- `AgentDeploy/register_agent.md` — this runbook for Salesforce admins.

---

## 2. Service Overview

- The REST API lives at `https://mcp-sample-p525.onrender.com`, exposing endpoints for document and index retrieval:
    - `GET /api/v1/indexes` — List available index fields and values
    - `POST /api/v1/search` — Search documents by index filters (supports numeric comparisons)
    - `GET /api/v1/documents/{doc_id}` — Retrieve document content (text or raw PDF)
    - `GET /api/v1/documents/{doc_id}/json` — Retrieve document text content as JSON (Salesforce compatible)
    - `GET /openapi.json` — OpenAPI schema for Salesforce External Service registration
    - `GET /docs` — Swagger UI for interactive testing

---

## 6. Salesforce External Service Registration Steps (Recommended)

To enable Salesforce to search and retrieve document text for answering user questions, follow these steps:

1. **Create a Named Credential**
  - Setup → Security → Named Credentials → New
  - Label/Name: `ContentMCPServer`
  - URL: `https://mcp-sample-p525.onrender.com`
  - Identity Type: Named Principal
  - Authentication Protocol: No Authentication (for demo)

2. **Create an External Service**
  - Setup → Integrations → External Services → New External Service
  - Service Name: `ContentMCPService`
  - Service Schema Source: From Endpoint (point at your server's `/openapi.json` endpoint)
  - Salesforce will prompt you to associate operations with supported media types. Only select operations that return `application/json`:
    - `get_indexes_api_v1_indexes_get`
    - `search_indexes_api_v1_search_post`
    - `get_document_json_api_v1_documents__doc_id__json_get` (the new endpoint for document text as JSON)
  - Do **not** select endpoints that return `text/html`, `text/plain`, or `application/pdf`.

3. **Add the External Service Actions to Your Agent**
  - In Agent Builder, add actions for:
    - Searching documents (`search_indexes_api_v1_search_post`)
    - Retrieving document text (`get_document_json_api_v1_documents__doc_id__json_get`)
  - Use the document text returned in the JSON response to answer user questions.

---

## Example: Retrieve Document Text as JSON

```http
GET /api/v1/documents/000001.pdf/json
Response:
{
  "doc_id": "000001.pdf",
  "content": "Extracted text here"
}
```

---



## 3. Validate the Hosted API


```powershell
# Health check
curl https://mcp-sample-p525.onrender.com/health

# List available index fields
  -d "{\"filters\":{\"invoice_amount\":[\">5000\"]}}"

# Retrieve raw PDF
curl https://mcp-sample-p525.onrender.com/api/v1/documents/000001.pdf?format=raw
start https://mcp-sample-p525.onrender.com/docs
```


---

---

## 4. Register the Tool in Salesforce Agentforce

> **Note:** Salesforce UI and available AgentForce menus vary by org. Some Developer Edition orgs do not expose a dedicated "Tools ▸ New Tool" workflow. If you do see **Setup ▸ Agentforce ▸ Tools ▸ New Tool**, follow the steps below. If not, use the alternate External Service + Agent Builder flow described after the primary steps.


### Primary (if you have the Tools UI):

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
---



---


### Alternate (recommended when "Tools" is not visible):

Many Developer Edition orgs should instead register your REST endpoints using Salesforce's Named Credential + External Service model and then reference the External Service actions from Agent Builder. This flow is functionally equivalent and is the recommended path when the "Tools" UI is absent.

**A. Create a Named Credential**
- Setup → Security → Named Credentials → New (or Legacy New)
- Label/Name: `ContentMCPServer`
- URL: `https://mcp-sample-p525.onrender.com`
- Identity Type: Named Principal
- Authentication Protocol: No Authentication (for demo)

**B. Create an External Service**
- Setup → Integrations → External Services → New External Service
- Service Name: `ContentMCPService`
- Service Schema Source: From Endpoint (point at your server's `/openapi.json` endpoint) or choose Manual Schema and paste a small OpenAPI snippet if Salesforce cannot fetch it.

**C. Create / configure your Agent and add the action**
- Setup → Agentforce Agents → New Agent (or open an existing agent in Agent Builder)
- In Agent Builder, create a Topic (or edit an existing Topic) and add an Action:
  - Add Action → API → External Services → `ContentMCPService` → select the search action (e.g., `search`)
  - Configure input parameters for `filters` (e.g., `customer`, `invoice_amount`) as text inputs per your schema.

---


**Notes & Troubleshooting**
- If External Service actions don't appear immediately in Agent Builder, wait 5–10 minutes for propagation, or try deactivating/reactivating the agent (Agent Builder locks edits while active).
- Ensure your MCP server exposes the OpenAPI endpoint and is reachable from Salesforce (public TLS certificate required). If Salesforce cannot fetch the OpenAPI, paste a minimal manual schema per the External Service creation form.
- You must be a System Administrator to create Named Credentials and External Services.
- See `docs/salesforce-agentforce-setup.md` for an expanded walkthrough and example manual OpenAPI schema.

---


---

## 5. Test the Integration

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


