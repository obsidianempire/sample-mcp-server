# Cloud Deployment for Salesforce Integration

> **Important:** Expose the HTTP endpoints by setting the environment variable `MCP_SERVER_MODE=http` for any container or server-based deployment. AWS Lambda sets `AWS_LAMBDA_FUNCTION_NAME` automatically, so no additional configuration is required there.

## Option 0: Render (Recommended for Quick Deployment)

Render is the easiest option for deploying this service with minimal configuration.

### Quick Setup

1. **Connect GitHub repository to Render**
   - Go to https://render.com and sign in
   - Click "New +" → "Web Service"
   - Select your GitHub repository
   - Render will auto-detect `render.yaml` configuration

2. **Render Service Configuration** (auto-configured via `render.yaml`)
   - Service URL: `https://your-service-name.onrender.com`
   - SSL certificate automatically provisioned
   - All endpoints available immediately

3. **Deploy**
   - Render automatically deploys on each push to your connected branch
   - Your service URL will be: `https://your-service-name.onrender.com`
   - All endpoints available at that base URL
   - SSL certificate automatically provisioned

4. **Verify Deployment**
   ```bash
   # Health check
   curl https://your-service-name.onrender.com/health
   
   # List indexes
   curl https://your-service-name.onrender.com/api/v1/indexes
   
   # Swagger UI
   open https://your-service-name.onrender.com/docs
   ```

5. **Configure Salesforce AgentForce**
   - Follow [docs/agentforce-content-service.md](../docs/agentforce-content-service.md) using your Render URL
   - Update Named Credential with: `https://your-service-name.onrender.com`

### Render-Specific Notes

- **Free tier**: Includes 750 hours/month
- **Pro tier**: Always-on deployment with better performance
- **Monitoring**: Built-in logs available in Render dashboard
- **Auto-scaling**: Available on Pro tier

---

## Option 1: AWS Lambda + API Gateway

1. **Package for Lambda:**
```bash
pip install -t . fastapi uvicorn mangum
```

2. **Create Lambda handler:**
```python
from mangum import Mangum
from src.content_mcp_server import app

handler = Mangum(app)
```

3. **Deploy to AWS Lambda**
4. **Create API Gateway** pointing to Lambda
5. **Configure custom domain** (required for Salesforce)

## Option 2: AWS ECS/Fargate

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY assets/ ./assets/
EXPOSE 10000
ENV MCP_SERVER_MODE=http
ENV PORT=10000
CMD ["python", "src/content_mcp_server.py"]
```

2. **Deploy to ECS/Fargate**
3. **Configure Application Load Balancer**
4. **Set up SSL certificate**
5. **Set task environment variable** `MCP_SERVER_MODE=http` so FastAPI app is available when the container starts

## API Endpoints Available After Deployment

### Document & Index Retrieval (New)
- `GET /api/v1/indexes` - List available index fields and values
- `POST /api/v1/search` - Search documents by index filters
- `GET /api/v1/documents/{doc_id}` - Retrieve document content (text or raw PDF)

### Salesforce Integration
- `GET /api/v1/actions` - OpenAPI schema for External Service registration
- `POST /api/v1/actions/search_content` - Banking services search endpoint
- `GET /health` or `GET /api/health` - Health check
- `GET /docs` - Swagger UI

## Salesforce Integration

### Named Credential Setup:
1. Go to **Setup → Named Credentials**
2. Create new credential:
   - **URL**: `https://your-render-url.onrender.com` (or AWS domain)
   - **Auth Type**: No Authentication (demo) or OAuth/API Key (production)
   - **Header** (if needed): `Authorization: Bearer your-api-key`

### Apex Integration:
```apex
public class ContentSearchHandler {
    /**
     * Search for documents by index filters
     */
    public static Map<String, Object> searchDocuments(Map<String, List<String>> filters) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:ContentMCP/api/v1/search');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        
        Map<String, Object> body = new Map<String, Object>();
        body.put('filters', filters);
        req.setBody(JSON.serialize(body));
        
        Http http = new Http();
        HttpResponse res = http.send(req);
        
        if (res.getStatusCode() == 200) {
            return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        }
        return null;
    }
    
    /**
     * Retrieve document content as text
     */
    public static String getDocumentText(String docId) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:ContentMCP/api/v1/documents/' + docId + '?format=text');
        req.setMethod('GET');
        Http http = new Http();
        HttpResponse res = http.send(req);
        return (res.getStatusCode() == 200) ? res.getBody() : null;
    }
}
```

## Security:
- Use proper API keys or OAuth for production
- Whitelist Salesforce IP ranges (optional)
- Enable HTTPS only (Render provides SSL by default)
- Implement CORS restrictions (see [agentforce-content-service.md](agentforce-content-service.md))
- Rate limiting recommended for production
- Enable HTTPS only
- Rate limiting recommended
