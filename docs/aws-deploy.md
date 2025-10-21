# AWS Deployment for Salesforce Integration

> **Important:** Expose the HTTP endpoints by setting the environment variable `MCP_SERVER_MODE=http` for any container or server-based deployment. AWS Lambda sets `AWS_LAMBDA_FUNCTION_NAME` automatically, so no additional configuration is required there.

## Option 1: AWS Lambda + API Gateway

1. **Package for Lambda:**
```bash
pip install -t . fastapi uvicorn mangum
```

2. **Create Lambda handler:**
```python
from mangum import Mangum
from content_mcp_server import app

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
EXPOSE 8000
CMD ["uvicorn", "src.content_mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Deploy to ECS/Fargate**
3. **Configure Application Load Balancer**
4. **Set up SSL certificate**
5. **Set task environment variable** `MCP_SERVER_MODE=http` so FastAPI app is available when the container starts

## Salesforce Integration

### Named Credential Setup:
1. Go to **Setup → Named Credentials**
2. Create new credential:
   - **URL**: `https://your-aws-domain.com`
   - **Auth Type**: Custom
   - **Header**: `Authorization: Bearer your-api-key`

### Apex Integration:
```apex
public class ContentMCPService {
    public static List<ContentItem> searchContent(String classes, String status, String customerId) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:ContentMCP/api/v1/content');
        req.setMethod('GET');
        req.setHeader('Content-Type', 'application/json');
        
        String params = '?classes=' + EncodingUtil.urlEncode(classes, 'UTF-8');
        if (String.isNotBlank(status)) {
            params += '&status=' + EncodingUtil.urlEncode(status, 'UTF-8');
        }
        if (String.isNotBlank(customerId)) {
            params += '&customer_id=' + EncodingUtil.urlEncode(customerId, 'UTF-8');
        }
        
        req.setEndpoint(req.getEndpoint() + params);
        
        Http http = new Http();
        HttpResponse res = http.send(req);
        
        if (res.getStatusCode() == 200) {
            Map<String, Object> result = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
            // Parse and return content items
        }
        
        return new List<ContentItem>();
    }
}
```

## API Endpoints for Salesforce:

- **GET** `/api/v1/content` - Search with query parameters
- **POST** `/api/v1/content/search` - Search with JSON body
- **GET** `/api/health` - Health check

## Security:
- Use proper API keys or OAuth
- Whitelist Salesforce IP ranges
- Enable HTTPS only
- Rate limiting recommended
