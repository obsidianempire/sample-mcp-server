# Render Deployment Quick Start

This document summarizes the Render deployment for the Content MCP Server.

## Overview

The Content MCP Server is configured to deploy on Render with a single push to GitHub. All deployment configuration is in `render.yaml` at the repository root.

## What's Been Updated

### Configuration Files
- **`render.yaml`** - Render service configuration with environment variables and build/start commands
  - Includes comments describing new API endpoints
  - Sets `MCP_SERVER_MODE=http` for REST API functionality
  - Configures Python 3.11 runtime

### Documentation
- **`README.md`** - Updated with new API endpoints and content retrieval service examples
- **`docs/aws-deploy.md`** - Expanded to include Render as the recommended deployment option (Option 0)
- **`docs/agentforce-content-service.md`** - Comprehensive guide for configuring Salesforce AgentForce to use the service

### New Capabilities
- Content retrieval service with PDF text extraction
- Index-based document filtering (supports numeric comparisons)
- RESTful APIs for integration with Salesforce AgentForce

---

## Deploying to Render

### Step 1: Connect GitHub to Render

1. Go to https://render.com
2. Sign in or create an account
3. Click **"New +"** → **"Web Service"**
4. Select your GitHub repository (`sample-mcp-server`)
5. Authorize Render to access your GitHub

### Step 2: Configure Service

Render will auto-detect `render.yaml` and apply these settings:

- **Service Name**: `content-mcp-server`
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/content_mcp_server.py`
- **Environment Variables**:
  - `PYTHON_VERSION=3.11.0`
  - `PORT=10000`
  - `MCP_SERVER_MODE=http`

### Step 3: Deploy

Click **"Create Web Service"** and Render will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Start the FastAPI server on port 10000
4. Provision an SSL certificate
5. Assign a public URL: `https://your-service-name.onrender.com`

### Step 4: Verify Deployment

Once deployment completes, test the service:

```bash
# Health check
curl https://your-service-name.onrender.com/health

# List available indexes
curl https://your-service-name.onrender.com/api/v1/indexes

# Test Swagger UI
open https://your-service-name.onrender.com/docs
```

### Step 5: Configure Salesforce AgentForce

Follow the detailed guide in `docs/agentforce-content-service.md` using your Render URL:
- **Named Credential URL**: `https://your-service-name.onrender.com`
- **External Service**: Point to `/api/v1/actions` endpoint

---

## Available Endpoints

### Document & Index Retrieval
- `GET /api/v1/indexes` - List index fields and available values
- `POST /api/v1/search` - Search documents by filters (supports `>`, `<` operators)
- `GET /api/v1/documents/{doc_id}?format=text|raw` - Retrieve document content

### Development & Testing
- `GET /` - Interactive test interface
- `GET /docs` - Swagger UI
- `GET /health` - Health check

### Salesforce Integration (Legacy)
- `POST /api/v1/actions/search_content` - Banking services search
- `GET /api/v1/actions` - OpenAPI schema for External Service registration

---

## Sample Data

The service includes pre-indexed PDF documents:

| Document | Customer | Invoice Amount | Balance |
|----------|----------|--------|---------|
| 000001.pdf | Acme Corp | 6000 | 1200 |
| 000002.pdf | XYY | 2000 | 0 |
| 000003.pdf | Beta LLC | 7500 | 500 |
| 000004.pdf | Gamma Inc | 4500 | 50 |

Text content extracted from PDFs is cached in `assets/texts/`.

### Example Queries

**Find invoices > 5000:**
```bash
curl -X POST https://your-service.onrender.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"filters": {"invoice_amount": [">5000"]}}'
```
Returns: `000001.pdf`, `000003.pdf`

**Find customer XYY:**
```bash
curl -X POST https://your-service.onrender.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"filters": {"customer": ["XYY"]}}'
```
Returns: `000002.pdf`

**Retrieve document text:**
```bash
curl https://your-service.onrender.com/api/v1/documents/000001.pdf?format=text
```

---

## Continuous Deployment

Render automatically deploys on every push to your connected branch:

1. Push changes to GitHub
2. Render detects the push
3. Builds and deploys automatically
4. New service URL is live (same URL, updated code)

No need to manually rebuild or redeploy!

---

## Render-Specific Features

### Free Tier
- 750 hours/month (covers 1 always-on service)
- Auto-spins down after 15 min of inactivity (cold starts on next request)
- Sufficient for development and testing
- Up to 0.5 GB memory

### Pro Tier
- Always-on service (no cold starts)
- Up to 16 GB memory
- Dedicated support
- Custom domains

### Monitoring & Logs
- View real-time logs in Render dashboard
- Export logs for external monitoring
- Alert on service failures

### Adding Custom Domain
1. In Render dashboard, go to your service
2. Click "Settings"
3. Add custom domain under "Custom Domain"
4. Update DNS CNAME to point to Render

---

## Troubleshooting

### Service won't deploy
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `src/content_mcp_server.py` has no syntax errors

### Service deploys but returns 500 errors
- View logs in Render dashboard
- Check for missing environment variables
- Verify `/health` endpoint returns 200

### Slow PDF extraction
- First request for a document's text is slow (PyPDF2 extracts on-demand)
- Subsequent requests are cached
- Consider upgrading to Pro tier if response time critical

### Can't reach Salesforce from service
- Verify HTTPS is being used (Render provides SSL by default)
- Check CORS settings (currently permissive, should restrict for production)
- Confirm Salesforce IP is not blocked

---

## Next Steps

1. ✅ Deploy to Render (push to GitHub, service auto-deploys)
2. ✅ Test endpoints via Swagger UI (`/docs`)
3. Configure Salesforce AgentForce (see `docs/agentforce-content-service.md`)
4. Add authentication for production (API keys or OAuth)
5. Restrict CORS origins to Salesforce domain
6. Monitor logs for errors and performance

---

## Support & Resources

- **Render Documentation**: https://render.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Salesforce AgentForce Setup**: See `docs/agentforce-content-service.md`
- **API Documentation**: Visit `/docs` on your deployed service for interactive Swagger UI

---

## Files Changed for Render Deployment

```
render.yaml                             (created)
README.md                               (updated)
docs/aws-deploy.md                      (updated)
docs/agentforce-content-service.md      (created)
scripts/preextract_texts.py             (created)
assets/indexes.json                     (created)
```

For a complete list of changes, see the git diff or review the updated documentation.
