# AgentForce Setup Guide for Salesforce Developer Edition

## Prerequisites

1. **Salesforce Developer Edition org** - [Sign up here](https://developer.salesforce.com/signup)
2. **Your MCP server deployed** - Use Render URL (e.g., `https://your-app.onrender.com`)
3. **Basic Salesforce knowledge** - Understanding of Setup, Objects, and Apps

## Step 1: Enable AgentForce (if not already enabled)

### 1.1 Check AgentForce Availability
```
Setup → Feature Settings → Einstein → Einstein Platform → Agent Builder
```
- If you don't see "Agent Builder", AgentForce might not be available in your org yet
- Try enabling Einstein features first

### 1.2 Enable Required Features
```
Setup → Company Information → Enable:
- Einstein Platform
- Einstein Discovery
- Einstein Conversation Insights
```

## Step 2: Create External Service Connection

### 2.1 Create Named Credential
```
Setup → Security → Named Credentials → Legacy → New
```

**Settings:**
- **Label**: `ContentMCPServer`
- **Name**: `ContentMCPServer`
- **URL**: `https://your-render-app.onrender.com`
- **Certificate**: Use system default
- **Identity Type**: Named Principal
- **Authentication Protocol**: Custom
- **Custom Headers**:
  - Name: `Content-Type`
  - Value: `application/json`

### 2.2 Create External Service
```
Setup → Integrations → External Services → New External Service
```

**Method 1: From Endpoint**
- **Service Name**: `ContentMCPService`
- **Endpoint URL**: `https://your-render-app.onrender.com/api/v1/actions`
- **Named Credential**: Select `ContentMCPServer`
- Click **Next** → Salesforce will auto-generate the service

**Method 2: Manual OpenAPI Schema**
If auto-generation fails, create this schema:

```yaml
openapi: 3.0.0
info:
  title: Content MCP Service
  version: 1.0.0
servers:
  - url: https://your-render-app.onrender.com/api/v1
paths:
  /actions/search_content:
    post:
      summary: Search Content Items
      parameters:
        - name: classes
          in: query
          required: true
          schema:
            type: string
          description: Comma-separated content classes
        - name: status
          in: query
          schema:
            type: string
          description: Filter by status (active, closed)
        - name: customer_id
          in: query
          schema:
            type: string
          description: Filter by customer ID
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
```

## Step 3: Create AgentForce Agent

### 3.1 Access Agent Builder
```
Setup → Feature Settings → Einstein → Agent Builder
```
OR
```
App Launcher (9 dots) → Agent Builder
```

### 3.2 Create New Agent
1. Click **New Agent**
2. **Agent Name**: `Content Search Agent`
3. **Description**: `Helps users search banking content like autopayments and standing instructions`
4. **Role**: `Assistant`

### 3.3 Configure Agent Instructions
```
You are a helpful banking content assistant. You help users find information about:
- Standing Instructions (recurring transfers)
- Autopayments (scheduled bill payments)
- Service Links (connected accounts and services)

When users ask about banking services, use the search_content action to find relevant information.

Always be helpful and provide clear explanations of the banking services you find.

If a user asks about a specific customer, make sure to filter by their customer ID.
```

### 3.4 Add Knowledge Base (Optional)
- Click **+ Add Knowledge**
- Upload documents about your banking services
- This helps the agent provide context

## Step 4: Configure Agent Actions

### 4.1 Add External Action
1. In Agent Builder, go to **Actions** tab
2. Click **+ Add Action**
3. Select **Flow** → **External Service**
4. Choose your `ContentMCPService`
5. Select `search_content` action

### 4.2 Configure Action Parameters
Map the parameters:
- **classes**: `Text` (required)
- **status**: `Text` (optional)
- **customer_id**: `Text` (optional)

### 4.3 Action Instructions
```
Use this action when users want to:
- Find autopayments for a customer
- Search for standing instructions
- Look up service links
- Get banking service information

Examples:
- "Show me all autopayments for customer C123"
- "Find standing instructions"
- "What services are linked for customer C456?"
```

## Step 5: Test Your Agent

### 5.1 Use Agent Builder Preview
1. Click **Preview** button in Agent Builder
2. Test queries like:
   - "Show me all autopayments"
   - "Find active services for customer C123"
   - "What standing instructions are there?"

### 5.2 Sample Test Conversations
```
User: "Show me autopayments for customer C123"
Agent: Uses search_content with classes=autopayment, customer_id=C123

User: "Find all active banking services"
Agent: Uses search_content with classes=standing_instruction,autopayment,service_link, status=active
```

## Step 6: Deploy Agent to Users

### 6.1 Activate Agent
1. In Agent Builder, click **Activate**
2. Choose deployment options:
   - **Experience Cloud Site**
   - **Salesforce Mobile App**
   - **Service Console**

### 6.2 Create Agent App (Optional)
```
Setup → Apps → App Manager → New Lightning App
```
- Add your agent as a tab
- Assign to user profiles

## Step 7: Monitor and Improve

### 7.1 Agent Analytics
```
Setup → Einstein → Agent Analytics
```
- View conversation metrics
- Identify common queries
- Optimize agent responses

### 7.2 Debugging
```
Setup → Debug → Debug Logs
```
- Monitor external service calls
- Check for API errors
- Verify data flow

## Common Issues & Solutions

### Issue: "External Service not found"
**Solution**: 
- Verify Named Credential is correct
- Check if your Render app is running
- Test the endpoint manually: `https://your-app.onrender.com/api/v1/actions`

### Issue: "AgentForce not available"
**Solution**:
- Check if your org has Einstein features enabled
- Some Developer Edition orgs may not have AgentForce yet
- Try using Flow + External Service as alternative

### Issue: "Action not working"
**Solution**:
- Check Debug Logs for API call details
- Verify endpoint URL is correct
- Test your MCP server endpoints directly

## Alternative: Flow-Based Solution

If AgentForce is not available, create a Flow instead:

### Flow Setup
```
Setup → Process Automation → Flows → New Flow
```

1. **Flow Type**: Screen Flow
2. **Add Screen**: "Search Banking Content"
3. **Add Components**:
   - Text Input: `classes`
   - Text Input: `customer_id`
   - Picklist: `status` (Active, Closed)
4. **Add Action**: Call your External Service
5. **Display Results**: Show returned data

This gives you similar functionality through Salesforce Flows.

## Testing Endpoints

Test your endpoints before integrating:

```bash
# Test actions list
curl https://your-app.onrender.com/api/v1/actions

# Test search action
curl -X POST "https://your-app.onrender.com/api/v1/actions/search_content?classes=autopayment&customer_id=C123"
```

## Next Steps

1. **Enhance Data**: Add more realistic banking data to your MCP server
2. **Add Security**: Implement proper API authentication
3. **Create Custom Objects**: Store search results in Salesforce
4. **Build Dashboard**: Visualize banking service usage
5. **Add Workflows**: Automate actions based on search results

## Support Resources

- [Salesforce AgentForce Documentation](https://help.salesforce.com/agentforce)
- [External Services Trailhead](https://trailhead.salesforce.com/en/content/learn/modules/external-services)
- [Salesforce Developer Documentation](https://developer.salesforce.com/docs)
