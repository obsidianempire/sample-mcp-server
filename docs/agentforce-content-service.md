
# AgentForce — Content Retrieval Mock Service

This document explains how to configure Salesforce AgentForce (latest developer tooling) to call the Mock Content Retrieval Service provided by this repository.

---

## Overview

- **Service base URL (local dev):** `http://<host>:<port>` (default port: `10000`)
- **FastAPI Swagger UI:** `http://<host>:<port>/docs`
- **OpenAPI (for Salesforce External Services):** `http://<host>:<port>/openapi.json`

---

## Provided Endpoints

### `GET /api/v1/indexes`
- Returns available index fields and example values. Useful for building filters in Agent UI.
- **Response:**

```json
{"success":true,"count":N,"fields":{...}}
```

### `POST /api/v1/search`
- Accepts JSON body `{ "filters": { "field": ["value", ">5000"] } }`
- Supports numeric comparisons for numeric fields using prefixes: `">5000"`, `"<100"`
- Returns matching document IDs:

```json
{"success":true,"count":X,"document_ids":[...]}
```

- **Example body to find invoices > 5000:**
```json
{
  "filters": {"invoice_amount": [">5000"]}
}
```

### `GET /api/v1/documents/{doc_id}?format=text|raw`
- `format=text` (default): returns the extracted text of the PDF.
- `format=raw`: returns the raw PDF as `application/pdf`.
- **Example:**
```
GET /api/v1/documents/000001.pdf?format=text
```

---

## Notes on CORS and Authentication
- This mock service sets permissive CORS in development mode (`allow_origins=['*']`). For production, restrict origins and add authentication.
- The mock service does not enforce auth. For real orgs, configure an authentication flow (Named Credential, OAuth, API Key) and add checks to the service.

---

## How to Register the Service in Salesforce (External Service / AgentForce)

1. **Start the mock service locally:**
    - Create a virtualenv and install dependencies from `requirements.txt`.
    - Run the server: set environment variables if desired, then run:
      ```sh
      python src/content_mcp_server.py
      ```
    - By default the app runs on port `10000`.

2. **Obtain the OpenAPI descriptor for External Service registration:**
    - The project exposes a standard OpenAPI JSON at:
      ```
      http://<host>:10000/openapi.json
      ```
    - Copy the JSON to a file or provide the URL to Salesforce if reachable from your org.

3. **Create an External Service or Named Credential:**
    - In Salesforce Setup, search "External Services" and click **New External Service**.
    - Provide the OpenAPI descriptor URL (or upload the JSON) and complete the External Service creation.

4. **Create an Auth Provider and Named Credential (if needed):**
    - If your mock enforces an API key, create a Named Credential with the header or auth settings.
    - For OAuth, create an Auth Provider and use that in the Named Credential.

5. **Use the registered External Service in an AgentFlow or Apex call.**
    - Use the generated Apex/Flow actions to call `/search` and then fetch documents using `/documents/{doc_id}`.

---

## Example AgentForce Flow Pattern

1. Call the External Service `search` action with a filter payload (e.g., `invoice_amount > 5000`).
2. Receive `document_ids` in the response.
3. For each document id, call `documents/{doc_id}` with `format=text` to obtain the textual content to answer user questions.

---

## Example Payloads

**Search invoices greater than 5000:**
```http
POST /api/v1/search
Body: {"filters": {"invoice_amount": [">5000"]}}
```

**Check whether customer XYY has a balance:**
```http
1. POST /api/v1/search with {"filters": {"customer": ["XYY"]}}
2. For returned document ids, GET /api/v1/documents/{doc_id}?format=text and inspect the text.
```

---

## Testing using Swagger UI
- Start the server and browse to `/docs` to test the endpoints interactively.
- Use `/api/v1/indexes` to discover available fields and values.

---

## Limitations and Next Steps
- This is a mock service with permissive CORS and no authentication.
- Index values live in `assets/indexes.json`. The service supports simple numeric comparison operators and exact string matches.
- For more advanced search, consider adding inverted-indexing, full-text search, or vector embeddings.

---

## Contact / Maintenance
- If you need help mapping AgentForce actions to your real service, update this doc and provide the production OpenAPI JSON and auth details.
