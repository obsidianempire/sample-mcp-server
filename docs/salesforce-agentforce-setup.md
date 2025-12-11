# AgentForce Setup Guide for Salesforce Developer Edition (Updated 2024)

## Prerequisites

1. **Salesforce Developer Edition org** - [Sign up here](https://developer.salesforce.com/signup)
2. **Your MCP server deployed via HTTP** - Use Render URL (e.g., `https://your-app.onrender.com`) and ensure the environment variable `MCP_SERVER_MODE=http` is set so the server exposes the REST endpoints
3. **AgentForce may not be available in all Developer Edition orgs yet**

**Note**: This integration uses HTTP REST API mode, not stdio. Set the `MCP_SERVER_MODE=http` environment variable (Render example does this via service settings) to ensure the server runs in HTTP mode.

## Step 1: Check AgentForce Availability

### 1.1 Current Status (as of 2024)
✅ **You have AgentForce available!** Since you see "Agentforce Agents", you can proceed with the full setup.

Navigate to:
```
Setup → Quick Find → "Agentforce Agents"
```
OR
```
App Launcher (9 dots) → Search "Agentforce"
```

### 1.2 Enable Required Features (Updated)
```
Setup → Einstein Setup → Enable:
- Einstein Platform Services
- Einstein Generative AI
- Agentforce (should already be enabled if you see the menu)
```

## Step 2: External Service Setup (Works with both AgentForce and Flows)

### 2.1 Create Named Credential (Updated Path)
```
Setup → Security → Named Credentials → Legacy → New Legacy
```

**Settings:**
- **Label**: `ContentMCPServer`
- **Name**: `ContentMCPServer`
- **URL**: `https://your-render-app.onrender.com`
- **Certificate**: Default Certificate
- **Identity Type**: Named Principal
- **Authentication Protocol**: **No Authentication** (select this option)
- **Generate Authorization Header**: Unchecked

**Note:** Since your MCP server doesn't require authentication for demo purposes, "No Authentication" is the correct choice. Custom Headers are not available with "No Authentication" protocol. In production, you would implement API key authentication and use a different protocol.

### 2.2 Test Your Endpoint First
Before creating External Service, test your HTTP endpoint:

```bash
# Test if your server returns OpenAPI schema
curl https://your-render-app.onrender.com/api/v1/actions

# Test the actual search endpoint
curl -X POST https://your-render-app.onrender.com/api/v1/actions/search_content \
  -H "Content-Type: application/json" \
  -d '{"classes": "autopayment", "customer_id": "C123"}'
```

### 2.3 Create External Service (Updated)
```
Setup → Integrations → External Services → New External Service
```

**Current Method:**
- **Service Name**: `ContentMCPService`
- **Service Schema Source**: **"From Endpoint"**
- **Endpoint URL**: `https://your-render-app.onrender.com/api/v1/actions`
- **Named Credential**: `ContentMCPServer`

If this fails with MCP error, use **Manual Schema**:

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
      operationId: searchContent
      summary: Search Content
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                classes:
                  type: string
                status:
                  type: string
                customer_id:
                  type: string
              required: [classes]
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
```

## Step 3: AgentForce Setup (Updated for Current Interface)

### 3.1 Access Agentforce Agents
```
Setup → Agentforce Agents
```
OR
```
App Launcher → Agentforce Agents
```

### 3.2 Create New Agent (Current Process)
1. Click **New Agent**
2. **Template Selection**: You'll see these options:

**Primary Template Choice:**
- **Agentforce Service Agent**: Select this for customer service scenarios

3. After selecting "Agentforce Service Agent", you'll see these sub-templates:

**Available Sub-Templates:**
- **Service Customer Verification**: For identity verification workflows
- **Account Management**: For account-related queries and updates  
- **General FAQ**: For general question-and-answer scenarios

**For Banking Content Search, choose:**
1. **"Agentforce Service Agent"** 
2. Then **"General FAQ"** (best fit for search and information retrieval)

**Why "General FAQ" is recommended:**
- Designed for information lookup and Q&A scenarios
- Good for explaining search results to customers
- Handles "I don't know" responses gracefully
- Appropriate conversation flow for banking inquiries

**Alternative if you want more account focus:**
- **"Account Management"** - if you plan to add account modification features later

**Alternative Templates (if Service Agent doesn't work):**
- **Agent for Setup**: More technical/administrative focused - not ideal for customer-facing banking queries
- **Custom Agent**: Blank slate - requires more manual configuration

4. **Agent Name**: `Banking Content Assistant`
5. **Description**: `Helps users search banking content like autopayments, standing instructions, and service links`
6. Click **Create**

**Why "Agentforce Service Agent" → "Customer Service":**
- Pre-configured for customer support conversations
- Includes helpful error handling and clarification patterns
- Professional tone appropriate for banking
- Built-in conversation flow for Q&A scenarios

**Template Differences:**
- **Service Agent**: Pre-configured for customer support with built-in conversation patterns
- **Sales Agent**: Includes sales-focused prompts and lead qualification flows
- **Custom Agent**: Blank slate - you define everything from scratch

### 3.3 Configure Agent Instructions

After creating your agent, you'll be taken to the **Agent Builder** interface. Here's where to add your instructions:

**If prompted for Role, use:**
- **Role**: `Customer Service Representative` or `Banking Assistant`
- **Alternative roles**: `Support Agent`, `Information Assistant`, or `Service Representative`

**If prompted for Topic, use:**
- **Topic**: `Banking Services` or `Financial Services`
- **Alternative topics**: `Account Information`, `Customer Support`, or `Banking Operations`

**Why these work well:**
- **Role**: Sets professional, helpful tone and indicates the agent assists rather than makes decisions
- **Topic**: Defines the domain of expertise (banking/financial services)
- Both align with banking industry standards and customer expectations

**Location of Instructions:**
1. In the Agent Builder, look for the **"Instructions"** section (usually on the left side or main panel)
2. OR look for a **"Prompt"** section 
3. OR you might see **"Agent Instructions"** or **"System Instructions"**

**Step-by-step:**
1. Click on your newly created agent to open Agent Builder
2. Look for one of these sections:
   - **Instructions** (most common)
   - **Prompt** 
   - **System Prompt**
   - **Agent Behavior**
3. Click **Edit** or the pencil icon next to the instructions
4. Replace the default template text with your banking-specific instructions

**In the Instructions/Prompt section, replace the default text with:**
```
You are a helpful banking assistant that helps customers and staff find banking service information.

You can search for:
- Standing Instructions: Recurring transfers between accounts
- Autopayments: Scheduled bill payments to external companies  
- Service Links: Connected external financial services

When users ask about banking services:
1. Use the search_content action to find relevant information
2. Always filter by customer ID when provided
3. Explain what each service does in simple terms
4. Ask if they need help managing or modifying any services

Example queries you can help with:
- "Show me autopayments for customer C123"
- "Find all standing instructions"
- "What services are linked for customer C456?"

Always be professional and helpful in your responses.
```

**Save your changes** by clicking **Save** or **Update**.

**Note:** The exact location and naming may vary slightly depending on your Salesforce version, but look for any section related to "Instructions," "Prompt," or "Behavior" in the Agent Builder interface.

### 3.4 Configure Topics and Actions

After setting up your agent instructions, configure Topics and Actions in Agent Builder:

**Step 1: Access Topics Tab**
1. In Agent Builder, click on the **Topics** tab
2. You'll see options to add topics for your agent's capabilities

**Step 2: Add Banking Topics**
When you click **Add Topic**, you'll see two options:

**Option 1: "Add from Asset Library"**
- Browse pre-built topics from Salesforce's library
- These are generic topics that might apply to banking
- Pros: Quick setup, proven templates
- Cons: May not fit your specific banking use case perfectly

**Option 2: "New Topic"** ← **Choose this for banking content search**
- Create custom topics specific to your banking services
- Gives you full control over topic configuration
- Better alignment with your MCP server functionality

**Recommendation: Select "New Topic"** because:
- Your banking content search is specific and unique
- You need topics that match your MCP server's search capabilities
- Custom topics allow precise control over when actions are triggered
- Better integration with your external service parameters

**After selecting "New Topic", you'll see the topic creation form where you can fill in the banking-specific fields as outlined below.**

**Step 3: Create Your First Topic (Start Simple)**
Create just ONE topic first to avoid conflicts:

**Topic 1: Banking Support (Simple Start)**
```
Name: Banking Support
Classification: Customer Support
Description: Help customers with banking service questions
Scope: Handle general banking questions and service lookups
Instructions: 
Help customers with banking service questions. Be professional and helpful.
When customers ask about banking services, assist them with finding information.
```

**When you click "Next" and see "Select the actions you want to include in your topic":**

**OPTION 1: Skip Actions for Now (Recommended)**
- Click **"Skip"** or **"Next"** without selecting any actions
- Complete the topic creation
- Resolve activation issues first
- Add actions later after the agent is active

**OPTION 2: Add Actions Now (If Available)**
- Look for **ContentMCPService.searchContent** in the list
- If you see it, select it and continue
- If you don't see it, skip for now

**Why skipping is often better:**
- Avoids action-related errors during topic creation
- Allows you to resolve agent activation issues first
- External services sometimes aren't visible until after agent activation
- You can always add actions later

**After completing topic creation:**
1. Save the topic
2. Try to activate the agent
3. Resolve any activation errors
4. Then come back and add actions to topics

**Step 4: Resolve Activation Issues Before Adding Actions**

You need to resolve these errors before the agent can use actions:

**Error 1: "Conflicting topics check is incomplete"**
- This happens when Salesforce is still analyzing your topics
- **Solution**: Wait 5-10 minutes after creating topics
- Create topics one at a time, not all at once
- Make each topic very different in scope

**Error 2: "Your agent isn't connected to an Agentforce Data Library"**
- **Solution**: Add a Knowledge connection
- Go to **Knowledge** tab in Agent Builder
- Click **Add Knowledge Source**
- If you don't have Knowledge Articles, create a simple one:
  ```
  Setup → Knowledge → Articles → New Article
  Title: "Banking Services Help"
  Content: "We offer autopayments, standing instructions, and service links."
  ```

**Error 3: "Einstein Bots not turned on"**
- **Solution**: Enable Einstein Bots (optional for basic functionality)
- Go to `Setup → Einstein → Einstein Bots → Enable`
- Or ignore this error if you only want AgentForce functionality

**Error 4: "No conversation escalation flow"**
- **Solution**: Create a simple escalation flow or ignore for demo
- Go to `Setup → Process Automation → Flows → New Flow → Record-Triggered Flow`
- Or add escalation instructions to your agent prompt

**Step-by-Step Resolution Process:**

1. **Create ONE simple topic** (as shown above)
2. **Add Knowledge source**: 
   ```
   Agent Builder → Knowledge tab → Add Knowledge Source
   Select any Knowledge Article or create one
   ```
3. **Wait 10 minutes** for topic analysis to complete
4. **When you see the activation dialog with warnings**, you have two options:

**RECOMMENDED: Click "Ignore & Activate"**
- Most of these warnings are optional for basic functionality
- Your agent will work for testing even with these warnings
- You can resolve them later after testing

**Alternative: Click "Review Activation Checklist"**
- This will show you detailed steps to resolve each issue
- More time-consuming but creates a "perfect" setup
- Not necessary for initial testing

**Why "Ignore & Activate" is often the right choice:**
- **"Conflicting topics check is incomplete"**: Just means Salesforce is still analyzing - not an error
- **"Agent isn't connected to Data Library"**: Optional - you can add Knowledge later
- **"Einstein Bots not turned on"**: Optional - you're using AgentForce, not Einstein Bots
- **"No conversation escalation flow"**: Optional - you can add escalation later

**After clicking "Ignore & Activate":**
1. Your agent should activate successfully
2. Test it with the Preview button
3. **Important**: Once active, you cannot edit topics through the normal interface
4. To add actions to topics, you need to use a different workflow

**Step 5: Add Actions to Active Agent Topics**

Once your agent is activated, Salesforce locks topic editing for stability. Here's how to add your MCP server actions:

**Method 1: Deactivate, Edit, Reactivate (Recommended)**
1. In Agent Builder, click **"Deactivate"** 
2. Edit your existing topic:
   - Click on the topic name
   - Go to "This Topic's Actions" tab
   - Click **Add Action**
   - Select **API** → **External Services** → **ContentMCPService** → **Search Content**

**When you see "Configure your action for Agent", fill in these fields:**

**Input Parameters Configuration:**
- **classes** (Text Input):
  - **Label**: "Content Classes"
  - **Description**: "Comma-separated content classes: standing_instruction, autopayment, service_link"
  - **Default Value**: "standing_instruction,autopayment,service_link"
  - **Required**: Yes ✓

- **status** (Text Input):
  - **Label**: "Status Filter" 
  - **Description**: "Filter by status: active or closed"
  - **Default Value**: (leave empty)
  - **Required**: No

- **customer_id** (Text Input):
  - **Label**: "Customer ID"
  - **Description**: "Customer ID to filter results (e.g., C123)"
  - **Default Value**: (leave empty)
  - **Required**: No

**Action Instructions for the Agent:**
```
Use this action to search banking content based on user requests:

- For autopayments: set classes="autopayment"
- For standing instructions: set classes="standing_instruction" 
- For service links: set classes="service_link"
- For all services: set classes="standing_instruction,autopayment,service_link"

Always include customer_id when the user mentions a specific customer.
Use status="active" for current services, status="closed" for historical services.

Extract customer ID from user queries like "for customer C123" or "customer C456".
```

**Body Instructions (for the action input):**
```
This action searches banking content items. Use the following guidelines:

1. classes parameter (required):
   - Use "autopayment" for bill payment queries
   - Use "standing_instruction" for transfer queries  
   - Use "service_link" for linked service queries
   - Use "autopayment,standing_instruction,service_link" for general searches

2. customer_id parameter (optional):
   - Extract from user input like "customer C123" or "for C456"
   - Required when user asks about specific customer data

3. status parameter (optional):
   - Use "active" for current/active services
   - Use "closed" for historical/cancelled services
   - Leave empty to search all statuses

Example inputs:
- User: "Show autopayments for C123" → classes="autopayment", customer_id="C123"
- User: "Find all services" → classes="autopayment,standing_instruction,service_link"
- User: "Active transfers for C456" → classes="standing_instruction", customer_id="C456", status="active"
```

**Response Code Instructions (for interpreting the response):**
```
The API returns a JSON response with this structure:
{
  "success": true,
  "result": {
    "items": [array of banking service items],
    "summary": "Found X items matching criteria",
    "metadata": {object with search details}
  }
}

How to handle the response:

1. Check if success=true, if false explain there was an error

2. Extract items from result.items array. Each item contains:
   - id: unique identifier
   - cls: service type (autopayment, standing_instruction, service_link)
   - text: human-readable description
   - indexes: metadata including status and customer_id

3. Present results in a user-friendly way:
   - Explain what each service type means
   - Include amounts and frequencies from the text
   - Group by service type if multiple types returned
   - If no results, suggest trying different search criteria

4. Always offer follow-up help:
   - "Would you like me to search for other types of services?"
   - "Do you need help with any of these services?"
   - "Would you like to see historical (closed) services as well?"

Example response handling:
- For autopayments: "I found 2 autopayments: $79.99 to Verizon monthly, and $55.00 to GymPro monthly."
- For no results: "I didn't find any autopayments for customer C123. Would you like me to check for standing instructions or service links instead?"
```

3. **Save the action configuration**
4. **Save the topic changes**
5. Click **"Activate"** again

# ...existing code...
If AgentForce is not available, create a Flow:

### 4.1 Create Screen Flow
```
Setup → Process Automation → Flows → New Flow → Screen Flow
```

### 4.2 Flow Structure
**Screen 1: Input**
- Text Input: Customer ID
- Picklist: Service Type (Autopayments, Standing Instructions, Service Links, All)
- Picklist: Status (Active, Closed, All)

**Action: External Service Call**
- External Service: `ContentMCPService`
- Action: `searchContent`
- Map inputs to parameters

**Screen 2: Results**
- Data Table or Text Template showing results

### 4.3 Deploy Flow
- Save and Activate
- Add to Lightning Page or create App

## Step 5: Testing and Deployment (Updated)

### 5.1 Test External Service First
Before connecting to AgentForce, verify your External Service works:

```
Setup → Integrations → External Services → ContentMCPService
```

1. Click **Test** button
2. Select `searchContent` operation
3. Use test payload:
```json
{
  "classes": "autopayment",
  "customer_id": "C123",
  "status": "active"
}
```
4. Verify you get a successful response

### 5.2 Test Your Agent
1. In the Agentforce Agents interface, find your agent
2. Click **Preview** button
3. Test with these sample queries that match your MCP server data:

**Basic Test Questions (should return results):**
- "Show me autopayments for customer C123"
  - Should find: $79.99 to Verizon monthly
- "Find all services for customer C123" 
  - Should find: 3 items (autopayment, standing instruction, service link)
- "What standing instructions exist for customer C123?"
  - Should find: $500 monthly transfer from Checking to Mortgage
- "Show me service links for customer C123"
  - Should find: Homeowners policy with Acme Insurance
- "Find autopayments for customer C789"
  - Should find: $55.00 to GymPro monthly

**Status Filter Tests:**
- "Show me active services for customer C123"
  - Should find 3 active services
- "Find closed services for customer C456" 
  - Should find: Closed Roth IRA at Delta Funds

**Edge Case Tests:**
- "Find services for customer C999"
  - Should return: "No services found for customer C999"
- "Show me all autopayments"
  - Should find autopayments for C123 and C789
- "What services are available?"
  - Should ask for customer ID

**Expected Response Format:**
The agent should respond with something like:
"I found 1 autopayment for customer C123: $79.99 to Verizon on the 15th monthly from Credit ****4242. Would you like me to search for other types of services or help you with anything else?"

### 5.3 Debug Agent Issues
If the agent doesn't work properly:

**Check Debug Logs:**
```
Setup → Environments → Debug → Debug Logs
1. Click "New" to create trace flag
2. Select your user
3. Set "Apex Code" to "DEBUG"
4. Set "Callout" to "DEBUG"
5. Test agent again
6. Check logs for errors
```

**Common Issues:**
- **"Action not found"**: Verify External Service is created and active
- **"Authentication failed"**: Check Named Credential configuration
- **"Timeout"**: Verify your Render app is running and responding
- **"Invalid response"**: Check if your API returns expected JSON format

### 5.4 Activate Your Agent
1. Click **Activate** in the agent builder
2. Choose deployment channels:
   - **Service Cloud Console**: For customer service reps
   - **Experience Cloud Site**: For customer self-service portal
   - **Slack Integration**: If you have Slack connected
   - **Embedded Chat**: For website integration

### 5.5 Configure Agent Permissions
```
Setup → Users → Permission Sets
```
1. Create new Permission Set: "AgentForce Banking Users"
2. Add permissions:
   - **Agentforce**: Enable agent access
   - **External Services**: Allow callouts to ContentMCPService
3. Assign to users who need access

### 5.6 Create Agent App Tab (Optional)
```
Setup → Apps → App Manager → New Lightning App
```
1. **App Name**: Banking Agent Assistant
2. **Developer Name**: Banking_Agent_Assistant
3. **Add Items**: 
   - Add "Agentforce Agents" tab
   - Add any custom objects you create
4. **User Profiles**: Assign to relevant profiles
5. **Save & Finish**

## Step 6: Advanced Configuration

### 6.1 Add Knowledge Base
Enhance your agent with additional context:

```
Setup → Knowledge → Knowledge Settings
```
1. Enable Knowledge if not already enabled
2. Create Knowledge Articles about banking services
3. In Agent Builder, go to **Knowledge** tab
4. Add Knowledge Articles as a data source

### 6.2 Create Custom Objects for Search Results
Store and track search results:

```
Setup → Object Manager → Create → Custom Object
```

**Object: Banking_Search_Result__c**
Fields:
- `Customer_ID__c` (Text, 50)
- `Search_Classes__c` (Text, 255)  
- `Results_Count__c` (Number)
- `Search_Timestamp__c` (DateTime)
- `Agent_Session_ID__c` (Text, 100)
- `Results_JSON__c` (Long Text Area, 32768)

### 6.3 Enhanced Agent Instructions
Update your agent with more sophisticated instructions:

```
You are an expert banking assistant with access to customer banking services data.

CAPABILITIES:
- Search standing instructions (recurring transfers)
- Find autopayments (scheduled bill payments)  
- Locate service links (external account connections)

CONVERSATION FLOW:
1. Greet the customer professionally
2. Ask for customer ID if not provided
3. Clarify what type of information they need
4. Use search_content action with appropriate filters
5. Explain results in customer-friendly language
6. Offer next steps or additional assistance

PARAMETER GUIDELINES:
- classes: Use specific values based on request
  * "standing_instruction" for transfers
  * "autopayment" for bill payments
  * "service_link" for linked accounts
  * Combine with commas for multiple types
- customer_id: Always required for customer-specific searches
- status: Use "active" for current services, "closed" for historical

RESPONSE FORMAT:
- Always explain what each service does
- Include relevant dates and amounts
- Ask if they want to modify or cancel any services
- Suggest related services they might be interested in

SECURITY:
- Never show services for other customers
- Always verify customer identity before showing sensitive data
- If customer ID is not provided, ask for it before searching

EXAMPLES:
User: "Show my autopayments"
Response: "I'd be happy to help you find your autopayments. Could you please provide your customer ID so I can search for your specific services?"

User: "Find autopayments for customer C123"  
Response: "Let me search for autopayments for customer C123..." [uses action] "I found 2 autopayments: [explains each one]. Would you like me to help you modify any of these?"
```

## Step 7: Production Considerations

### 7.1 Security Enhancements
**API Authentication:**
Update your MCP server to require proper authentication:

```python
# Add to your server
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        api_key = request.headers.get("Authorization")
        if not api_key or api_key != "Bearer your-secure-api-key":
            raise HTTPException(status_code=401, detail="Unauthorized")
    response = await call_next(request)
    return response
```

**Update Named Credential:**
```
Setup → Named Credentials → ContentMCPServer → Edit
Add Custom Header:
- Name: Authorization
- Value: Bearer your-secure-api-key
```

### 7.2 Monitoring and Analytics
**Create Dashboard:**
```
App Launcher → Analytics Studio
```
1. Create dataset from Banking_Search_Result__c
2. Build dashboard with:
   - Search volume over time
   - Most popular service types
   - Customer usage patterns
   - Agent performance metrics

**Set Up Alerts:**
```
Setup → Process Automation → Platform Events
```
1. Create Platform Event for failed searches
2. Set up Flow to send notifications
3. Monitor API errors and timeouts

### 7.3 Performance Optimization
**Caching Strategy:**
```python
# Add to your MCP server
from functools import lru_cache
import time

@lru_cache(maxsize=1000)
def cached_search(classes, customer_id, status, timestamp):
    # Cache results for 5 minutes (timestamp // 300)
    return perform_actual_search(classes, customer_id, status)

# Use in your endpoint
timestamp = int(time.time()) // 300  # 5-minute buckets
result = cached_search(classes, customer_id, status, timestamp)
```

## Step 8: Testing Scenarios

### 8.1 Functional Tests
Test these scenarios with your agent:

**Basic Search Tests:**
- "Show me autopayments for customer C123"
- "Find standing instructions for customer C456"  
- "What service links exist for customer C789"
- "Show all active services for customer C123"

**Edge Case Tests:**
- "Find services for customer INVALID" (should handle gracefully)
- "Show me unicorns" (should ask for clarification)
- Empty search results (should explain no results found)
- Very long customer ID or invalid format

**Security Tests:**
- Try to access other customer data
- Test without providing customer ID
- Test with malformed requests

### 8.2 Performance Tests
**Load Testing:**
```bash
# Use curl to test multiple concurrent requests
for i in {1..10}; do
  curl -X POST https://your-app.onrender.com/api/v1/actions/search_content \
    -H "Content-Type: application/json" \
    -d '{"classes": "autopayment", "customer_id": "C123"}' &
done
wait
```

**Response Time Monitoring:**
- Set up monitoring for API response times
- Alert if responses take longer than 5 seconds
- Monitor Render app performance metrics

## Step 9: Troubleshooting Guide

### 9.1 Common Agent Issues

**Issue: External Service not appearing in action list**
**Solution**: 
1. **Verify External Service exists and is active:**
   ```
   Setup → Integrations → External Services → ContentMCPService
   ```
   - Check that the service shows "Active" status
   - Click "Test" to verify it's working
   - If not active, edit and save the service

2. **Check Named Credential:**
   ```
   Setup → Security → Named Credentials → Legacy → ContentMCPServer
   ```
   - Verify URL is correct (your Render app URL)
   - Test the endpoint manually

3. **Refresh Agent Builder:**
   - Close and reopen Agent Builder
   - Or refresh the browser page
   - External services sometimes take a few minutes to appear

**Issue: "This agent's configuration has issues" during activation**
**Solutions for each error:**

**"Overlapping topics check is incomplete":**
- Wait a few minutes - Salesforce is still analyzing your topics
- Ensure each topic has unique, distinct instructions
- Make topic scopes more specific and non-overlapping
- Try saving topics individually, then check again

**"Conflicting topics check is incomplete":**
- Similar to overlapping - wait for analysis to complete
- Review your topic instructions for conflicts
- Make sure each topic handles different scenarios
- Example fix:
  ```
  Topic 1: "Handle autopayment queries only"
  Topic 2: "Handle standing instruction queries only" 
  Topic 3: "Handle general banking questions not covered by other topics"
  ```

**"Your agent isn't connected to an Agentforce Data Library":**
- This is often optional for basic functionality
- To resolve: Go to **Knowledge** tab in Agent Builder
- Add connection to Account or Contact objects
- Alternative: Ignore this warning if your agent works in Preview

**Step-by-step resolution:**

1. **Fix External Service visibility:**
   ```
   Setup → Integrations → External Services → ContentMCPService → Edit → Save
   ```

2. **Wait for topic analysis (5-10 minutes):**
   - Salesforce analyzes topics in background
   - Check back in Agent Builder after waiting

3. **Add minimal Knowledge connection:**
   ```
   Agent Builder → Knowledge tab → Add Knowledge → 
   Select any existing Knowledge Article or create a simple one
   ```

4. **Try activation again:**
   - Most warnings can be ignored if Preview works
   - Agent may activate with warnings

**If External Service still doesn't appear:**

1. **Create a simple test endpoint first:**
   Test your MCP server directly:
   ```bash
   curl -X POST https://your-render-app.onrender.com/api/v1/actions/search_content \
     -H "Content-Type: application/json" \
     -d '{"classes": "autopayment"}'
   ```

2. **Recreate External Service with minimal schema:**
   ```yaml
   openapi: 3.0.0
   info:
     title: Test Service
     version: 1.0.0
   paths:
     /actions/search_content:
       post:
         operationId: searchContent
         requestBody:
           content:
             application/json:
               schema:
                 type: object
                 properties:
                   classes:
                     type: string
         responses:
           '200':
             description: Success
             content:
               application/json:
                 schema:
                   type: object
   ```

3. **Check Salesforce logs:**
   ```
   Setup → Debug → Debug Logs
   Create trace flag → Test External Service → Check logs for errors
   ```

## Step 9: Using the AskMe Endpoint (External Service Integration)

### 9.1 Overview

The `/askme` endpoint is a specialized REST API that proxies questions to an external Mobius service. This allows your AgentForce agent to leverage external question-answering capabilities while maintaining conversation context.

### 9.2 Environment Variables Setup

The `/askme` endpoint requires only service configuration in environment variables. **Credentials are passed via HTTP Basic Auth header** in each request.

Required environment variables:

| Variable | Description | Where to Set |
|----------|-------------|--------------|
| `MOBIUS_SERVER` | Hostname of Mobius service | Render/AWS environment settings |
| `MOBIUS_PORT` | Port number (typically 8443) | Render/AWS environment settings |
| `MOBIUS_REPOSITORY_ID` | Repository ID for queries | Render/AWS environment settings |
| `MOBIUS_CERT_CONTENT` | (Optional) SSL certificate content as a string (recommended for self-signed certs) | Render/AWS environment settings |
| `MOBIUS_CERT_PATH` | (Optional) Path to SSL certificate file | Render/AWS environment settings |

**Setting in Render:**
1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add the variables listed above
4. Redeploy the service to apply changes

**Note:** Credentials are NOT stored in environment variables. They are passed via HTTP Basic Authorization header in each `/askme` request, allowing different users to authenticate with their own credentials.

#### 9.2.1 SSL Certificate Setup (For Self-Signed Certificates)

If your Mobius service uses a self-signed SSL certificate, you have two options:

**Option A: Use Certificate Content (Recommended for Render)**

This approach is easiest for cloud deployments as it doesn't require file management.

**Step 1: Extract the Certificate Content**

Run this command on your local machine or from a terminal with access to the Mobius server:

```bash
openssl s_client -connect <MOBIUS_SERVER>:<MOBIUS_PORT> -showcerts < /dev/null | openssl x509 -outform PEM > mobius-cert.pem
```

Example:
```bash
openssl s_client -connect services-us-virginia-m-1.skytap.com:9846 -showcerts < /dev/null | openssl x509 -outform PEM > mobius-cert.pem
```

**Step 2: View the Certificate Content**

```bash
cat mobius-cert.pem
```

Copy the entire certificate text (including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----` lines).

**Step 3: Set Environment Variable in Render**

In your Render service dashboard:
1. Navigate to **Environment** tab
2. Click **Add Environment Variable**
3. Set:
   - **Key**: `MOBIUS_CERT_CONTENT`
   - **Value**: Paste the entire certificate content from Step 2
4. Redeploy the service

**Advantages:**
- No file deployment issues
- Easy to update in cloud environments
- No .gitignore or file tracking concerns

---

**Option B: Use Certificate File Path**

This approach requires the certificate to be deployed with your application.

**Step 1: Extract the Certificate**

```bash
openssl s_client -connect <MOBIUS_SERVER>:<MOBIUS_PORT> -showcerts < /dev/null | openssl x509 -outform PEM > mobius-cert.pem
```

**Step 2: Add Certificate to Your Repository**

1. Create a `certs/` directory in your project root:
   ```bash
   mkdir certs
   ```

2. Copy the `mobius-cert.pem` file into this directory:
   ```bash
   cp mobius-cert.pem certs/
   ```

3. Ensure it's in git (not in .gitignore):
   ```bash
   git add certs/mobius-cert.pem
   git commit -m "Add Mobius service SSL certificate"
   git push
   ```

**Step 3: Set Environment Variable in Render**

In your Render service dashboard:
1. Navigate to **Environment** tab
2. Add new environment variable:
   ```
   MOBIUS_CERT_PATH=/app/certs/mobius-cert.pem
   ```
3. Redeploy the service

**Advantages:**
- Certificate is version-controlled
- Clear audit trail
- Easy to rotate with git history

---

**Troubleshooting SSL Certificate Issues:**

| Error | Cause | Solution |
|-------|-------|----------|
| "SSL: CERTIFICATE_VERIFY_FAILED" | Certificate not provided or incorrect | Set either `MOBIUS_CERT_CONTENT` or `MOBIUS_CERT_PATH` |
| "Could not find a suitable TLS CA certificate bundle" | Certificate file path doesn't exist at deployment | Use Option A (MOBIUS_CERT_CONTENT) or ensure git commits the file |
| "certificate verify failed: self-signed certificate" | Certificate not recognized | Verify the certificate matches your Mobius server |
| "Max retries exceeded" | SSL verification failed even with certificate | Re-extract the certificate, it may have changed |

**Recommended: Use Option A (MOBIUS_CERT_CONTENT)** for Render deployments as it's simpler and more reliable.

### 9.3 Using AskMe in Your Agent

#### Creating an External Service for AskMe

1. **Create Named Credential (if different from content service):**
   ```
   Setup → Security → Named Credentials → Legacy → New Legacy
   ```
   - **Label**: `MobiusAskMe`
   - **URL**: Your MCP server URL (e.g., `https://your-app.onrender.com`)
   - **Authentication Protocol**: **No Authentication**

2. **Create External Service:**
   ```
   Setup → Integrations → External Services → New External Service
   ```
   - **Service Name**: `AskMeService`
   - **Service Schema Source**: **Manual Schema**
   - **Named Credential**: `MobiusAskMe`
   - **OpenAPI Schema**:
   ```yaml
   openapi: 3.0.0
   info:
     title: AskMe Service
     version: 1.0.0
   servers:
     - url: https://your-app.onrender.com
   paths:
     /askme:
       post:
         operationId: askMe
         summary: Ask a question and get an answer with conversation context
         security:
           - basicAuth: []
         requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 required:
                   - userQuery
                 properties:
                   userQuery:
                     type: string
                     description: The question to ask
                   conversation:
                     type: string
                     description: Optional conversation history for context
         responses:
           '200':
             description: Successful response
             content:
               application/json:
                 schema:
                   type: object
                   properties:
                     answer:
                       type: string
                       description: The answer to the user's question
                     context:
                       type: object
                       properties:
                         conversation:
                           type: string
                           description: Updated conversation context
           '401':
             description: Missing or invalid Authorization header
           '400':
             description: Missing required fields
           '500':
             description: Server error (check environment variables)
           '502':
             description: Mobius service error
           '503':
             description: Connection error or SSL issue
           '504':
             description: Mobius service timeout
   components:
     securitySchemes:
       basicAuth:
         type: http
         scheme: basic
         description: HTTP Basic Authentication with Mobius username and password
   ```

3. **Add to Agent in Agent Builder:**
   - Open your Agent
   - Go to **Topics** tab
   - Create or edit a topic
   - Click **Add Action** → **API** → **External Services** → `AskMeService` → `askMe`
   - Map inputs:
     - `userQuery`: Input from user or previous action result
     - `conversation`: Use a variable to track conversation state
   - The Basic Auth header is automatically handled by Salesforce using the Named Credential

#### 9.4 Example Agent Topic Configuration

```
Topic: "Answer General Questions"
Condition: User asks questions not covered by other topics

Actions:
1. Ask Me Action:
   - Input: userQuery = "{user message}"
   - Input: conversation = "{stored conversation variable}"
   - Basic Auth credentials come from the Named Credential "MobiusAskMe"
   - Store result in a variable for future turns
   
2. Send Response:
   - Output: "Answer from Mobius: {ask me action result.answer}"
   - Update conversation variable: "{ask me action result.context.conversation}"
```

#### 9.5 How Basic Auth Works with Salesforce

1. **Named Credential** holds the base URL only (no credentials needed)
2. **Each request to `/askme`** includes:
   - Authorization header with the logged-in user's Mobius credentials
   - Request body with userQuery and conversation
3. **Your MCP server** extracts the credentials from the Authorization header and passes them to Mobius
4. **Mobius authenticates** the user with their provided credentials

This allows Salesforce to send each user's own credentials without storing them in environment variables.

#### 9.6 Passing Credentials from Salesforce

To send each user's Mobius credentials:

1. **Store credentials in Salesforce:**
   - Create custom contact/user fields:
     - `Mobius_Username__c` (text field)
     - `Mobius_Password__c` (encrypted field - recommended)

2. **In Agent Builder, map the Named Credential:**
   - Select the `MobiusAskMe` Named Credential
   - Override Authentication if needed (though typically not required for proxy pattern)
   - Alternatively, create a custom integration that builds the Authorization header

3. **If using a custom action:**
   ```apex
   // In Apex or Flow, construct the Authorization header:
   String credentials = username + ':' + password;
   String encoded = EncodingUtil.base64Encode(Blob.valueOf(credentials));
   String authHeader = 'Basic ' + encoded;
   
   // Then pass this in the HTTP request to /askme
   ```

#### 9.7 Security Considerations

- ✅ **Good**: Credentials are passed per-request, not stored in environment variables
- ✅ **Good**: Use HTTPS for all communications
- ✅ **Good**: Store passwords in Salesforce encrypted fields
- ✅ **Good**: Use field-level security to restrict access
- ⚠️ **Warning**: Ensure the connection between Salesforce and your MCP server is over HTTPS
- ⚠️ **Warning**: Consider using temporary tokens instead of passwords if Mobius supports them

**Issue: "Missing required environment variables"**
- Verify all 5 MOBIUS_* environment variables are set in Render/AWS
- Restart/redeploy the service after adding variables
- Check that variable names are exactly as listed (case-sensitive)

**Issue: "Missing Authorization header"** (401)
- The `/askme` request must include an Authorization header with Basic Auth
- Verify the Named Credential is properly configured in Salesforce
- Ensure Salesforce is sending the Authorization header in the External Service action

**Issue: "Invalid Authorization header format"** (401)
- The Authorization header must be in format: `Basic base64(username:password)`
- Verify credentials are properly base64 encoded
- Check that username and password don't contain special characters that need escaping

**Issue: "Failed to connect to Mobius service"**
- Verify `MOBIUS_SERVER` and `MOBIUS_PORT` are correct
- Check network connectivity from your deployment environment to Mobius server
- Ensure Mobius service is running and accessible
- Verify SSL certificate is valid (if using HTTPS)
- Check that the credentials passed have permission to access Mobius

**Issue: "Request timed out"** (504)
- Increase timeout handling in your topic logic
- Check Mobius service response time
- Verify network latency
- Check Mobius service is not overloaded

**Issue: "Invalid response from Mobius service"**
- Verify the response format matches expected JSON structure
- Check that Mobius service returns `answer` and `context.conversation` fields
- Review server logs for parsing errors
- Ensure the Mobius service endpoint is correct

## Step 10: Creating an Agent that Routes Financial Queries to AskMe

This step shows how to create a Salesforce AgentForce agent that routes banking-related questions to the `/askme` endpoint while maintaining conversation context.

### 10.1 Overview

The agent will:
1. Listen for user questions
2. Determine if the question is about banking statements, financial records, or loans
3. Forward qualifying questions to the `/askme` endpoint (unchanged)
4. Display the answer from Mobius to the user
5. Store the conversation context for the next user message
6. Reuse the stored context on subsequent requests

### 10.2 Step-by-Step Setup

#### Step 10.2.1: Create or Verify External Service for AskMe

First, ensure you have the `AskMeService` External Service configured (from Step 9). If you haven't already created it:

```
Setup → Integrations → External Services → New External Service
```

- **Service Name**: `AskMeService`
- **Service Schema Source**: **Manual Schema**
- **Named Credential**: Create a new one if needed:
  - Label: `MobiusAskMeCredential`
  - URL: `https://your-app.onrender.com`
  - Authentication Protocol: **No Authentication**

#### Step 10.2.2: Create a Custom Object to Store Conversation Context

Create a custom object to persist conversation state between user interactions:

```
Setup → Object Manager → Create → Custom Object
```

**Custom Object Details:**
- **Label**: `Agent Conversation Context`
- **Plural Label**: `Agent Conversation Contexts`
- **Object Name**: `Agent_Conversation_Context`
- **Record Name Field**: `Name` (auto-created)

**Add Custom Fields:**
1. **Conversation Data** (Long Text Area)
   - Field Label: `Conversation_Data`
   - Length: 32000
   
2. **User** (Lookup to User)
   - Field Label: `User`
   - Lookup Object: `User`
   - Allow lookup record to be deleted: Unchecked

3. **Last Updated** (Date/Time)
   - Field Label: `Last_Updated`
   - Auto-populate with current date and time

**Add a Custom List View:**
- Create a filter to show records for the current user
- This helps during testing

#### Step 10.2.3: Create an Agent in Agent Builder

**How to Access Agentforce Builder:**

1. Go to **Setup** (click gear icon) → Search for "Agentforce Agents"
2. Click on **Agentforce Agents** in the search results
3. Click the **New Agent** button (blue button at top right)
4. This opens **Agentforce Builder** (the tool where you'll create and configure the agent)

**Understanding the Agentforce Builder Interface:**

Once inside Agentforce Builder, you'll see a left sidebar with these tabs:
- **Topics** (hashtag icon) - Where you create topics that handle user intents
- **Data** (book icon - currently selected in your view) - Where you set up agent variables
- **Connections** - External services and API calls
- **Context** - Agent context settings
- **Language** - Localization settings
- **Events** - Logging and monitoring

**Note:** "Agentforce Builder" and "Agent Builder" refer to the same interface.

Navigate to:
```
Setup → Agentforce Agents → New Agent
```

**Agent Configuration:**
- **Name**: `Financial Query Agent` (or similar)

**Description** (Describe the agent's job in more detail - up to 929 characters):
```
Handles questions about banking statements, financial records, loans, and other financial matters. Routes complex queries to the Mobius knowledge base for detailed analysis and maintains conversation context for follow-up questions.
```

**Role** (Job description - what role it plays in your company - up to 184 characters):

Use this format starting with "You are...":

```
You are a financial services assistant supporting customers and internal staff with banking inquiries, loan information, and account documentation.
```

Or customize to your company:
```
You are a Financial Advisor helping users understand their banking statements, loan options, and account services.
```

**Company** (Tell the agent about your company - up to 85 characters):

Replace with YOUR company information:

```
Rocket Software, Inc. The company maintains content in a content repository. Using Askme allows the user to ask questions about content that they have permissions to ask.
```

Or example for a bank:
```
ABC Bank provides comprehensive financial services including checking, savings, loans, and investment products to customers nationwide.
```

**Optional Instructions** (in Agent Builder, look for "Instructions" or "System Prompt"):
```
You are a financial knowledge assistant. When users ask about banking statements, financial records, loans, or related financial topics, you provide accurate, helpful information from the Mobius knowledge base. Always maintain context from previous messages in the conversation to provide coherent, consistent responses across multiple user interactions.
```

**Enhanced Event Logs** (Optional):
- Check "Keep a record of conversations with enhanced event logs to review agent behavior" if you want detailed logging of agent interactions

#### Step 10.2.4: Set Up Agent Variables

**Note:** In Agentforce Builder, variables may be created implicitly when you configure actions, or they may be in a different location than shown in older documentation. 

For now, proceed with creating your topic and actions. You can reference variable names like `{user_question}`, `{conversation_context}`, `{mobius_answer}`, and `{ask_me_response}` in your action mappings, and they will be created as needed.

**Skip this step for now** - you'll reference these variables when configuring actions in the topic.

#### Step 10.2.5: Create a Topic for Financial Queries

**How to Access Topics:**

1. In Agentforce Builder, click the **Topics** tab (hashtag icon # on the left sidebar)
2. Click **New Topic** (or **+** button to create a new topic)

**Configure the Topic:**

1. **Name**
   - Value: `Financial Query Handler`
   - This is the display name for the topic in Agent Builder

2. **API Name**
   - Value: `Financial_Query_Handler`
   - Auto-generated from Name, but you can customize it
   - Used in code/API calls
   - Use underscores, no spaces

3. **Classification**
   - Value: `Financial Services`
   - Describes what category this topic falls under
   - Other examples: `Banking`, `Loan Inquiry`, `Account Services`

4. **Description**
   - Value: `Handles user questions about banking statements, financial records, loans, and account information. Routes inquiries to the Mobius service for detailed analysis and maintains conversation context for follow-up questions.`
   - Explains the purpose of the topic
   - Helps other admins understand what this topic does

5. **Scope** (Choose one)
   - Value: `Agent-specific` (recommended)
   - Other options: `Global` (shared across agents)
   - Use Agent-specific if this topic is only for this agent
   - Use Global if multiple agents need this topic

6. **Instructions** (Multiple instructions can be provided)

   **Instruction 1: Primary Role Definition**
   ```
   You are a financial services assistant. Your primary responsibility is to help users 
   with questions about:
   - Banking statements and transaction history
   - Financial records and account information
   - Loans and loan-related inquiries
   - Account balances and financial summaries
   
   When a user asks about these topics, you will extract their exact question and 
   forward it to the Mobius service for comprehensive analysis and answers.
   ```

   **Instruction 2: Conversation Management**
   ```
   Maintain conversation context across multiple user messages:
   - On the first user message, conversation context will be empty
   - After each response from Mobius, a conversation context will be provided
   - Use the stored conversation context when the user asks follow-up questions
   - This allows you to understand references like "that", "those", "the previous one", etc.
   
   Example: If user asks "What was my balance in July?" and then asks "Can you break 
   that down by week?", the conversation context helps understand "that" refers to 
   the July balance.
   ```

   **Instruction 3: Question Handling**
   ```
   For all financial questions received:
   - Extract the user's question exactly as asked (don't rephrase)
   - Include any relevant context the user provides (dates, account types, etc.)
   - Pass the question to the AskMe action
   - Wait for the response from Mobius
   - Present the answer to the user in a clear, professional manner
   - Do NOT modify, summarize, or interpret the Mobius response - present it as-is
   ```

   **Instruction 4: Error Handling**
   ```
   If the AskMe service fails:
   - Do NOT retry automatically
   - Inform the user: "I'm unable to process your financial inquiry at this time. 
     Please try again in a moment or contact support."
   - Do NOT attempt to answer the question yourself
   - Do NOT provide generic financial advice
   ```

**Topic Trigger Conditions:**

The agent will automatically trigger this topic when the user mentions:
- "banking"
- "statement" or "statements"
- "financial"
- "loan"
- "balance"
- "transaction" or "transactions"
- "account"
- "deposit"
- "withdrawal"
- "credit"
- "debit"

You can add more trigger keywords as needed based on your use cases.

#### Step 10.2.6: Add Actions to the Topic

Click **Add Action** and configure the following sequence:

**Action 1: Get Current Conversation Context**

This retrieves stored context for the current user. Since this is the first action with no previous action to reference, use **Apex** instead of Flow.

- **Action Type**: **Apex**
- **Reference Action Category**: **Apex Invocable Actions** (NOT "Apex REST (Beta)")
- **Purpose**: Load the `Agent_Conversation_Context` record for the current user
- **Output**: Store in `conversation_context` variable

**Agent Builder Configuration for this Action:**

1. **Agent Action Instructions** (What the agent should understand about this action):
   ```
   Retrieve the stored conversation context for the current user. This loads any previous conversation history so that follow-up questions can reference earlier messages.
   ```

2. **Loading Text** (Message shown while the action runs):
   ```
   Loading conversation history...
   ```

3. **Input Mapping Instructions** (How to configure inputs):
   - This Apex action has no required inputs
   - Leave all input fields empty or unmapped

4. **Output Mapping Instructions** (How to use the returned value):
   - **Output Variable Name**: Select or create `conversation_context`
   - **Output Data Type**: Text (Large Text Area)
   - **Mapping**: Map the returned context string to the `conversation_context` variable
   - This variable will contain the previous conversation data (or empty string if no prior context exists)

**Apex Implementation:**

Create this Apex class in your org (deploy via Developer Console or Salesforce CLI):

```apex
public class GetConversationContext {
    @InvocableMethod(label='Get User Conversation Context' description='Retrieves stored conversation context for the current user')
    public static List<String> getContext(List<GetContextRequest> requests) {
        List<String> results = new List<String>();
        String userId = UserInfo.getUserId();
        
        try {
            // Query the custom object - adjust the name to match YOUR org's custom object
            List<SObject> contexts = Database.query(
                'SELECT Conversation_Data__c FROM Agent_Conversation_Context__c WHERE User__c = \'' + userId + '\' LIMIT 1'
            );
            
            if (contexts.size() > 0) {
                Object contextData = contexts[0].get('Conversation_Data__c');
                results.add(contextData != null ? (String)contextData : '');
            } else {
                results.add('');
            }
        } catch (Exception e) {
            // If object doesn't exist or query fails, return empty context
            System.debug('Error retrieving conversation context: ' + e.getMessage());
            results.add('');
        }
        
        return results;
    }
    
    public class GetContextRequest {
        @InvocableVariable(label='Unused' required=false)
        public String unused;
    }
}
```

**Important:** If your custom object has a different name than `Agent_Conversation_Context__c`, change line 10 to match. For example:
- If you named it `Conversation_Context__c`: Change to `FROM Conversation_Context__c`
- If you named it `Agent_Context__c`: Change to `FROM Agent_Context__c`

Check your custom object's **API Name** in Setup > Custom Objects and use the exact API name in the query.

Then in Agent Builder:
- Select this Apex action
---

**Action 2: Call AskMe Service**

Now that you have context from Action 1, invoke the `/askme` endpoint:

- **Action Type**: **API** (or Apex wrapper if you get schema errors)
- **Service**: `AskMeService`
- **Operation**: `askMe`
- **Input Mapping**:
  - `userQuery`: `{user_question}` (the user's exact question)
  - `conversation`: `{conversation_context}` (context from previous requests, populated by Action 1)
- **Output Mapping**:
  - `answer`: Map to `mobius_answer` variable
  - `context`: This may cause schema errors - see troubleshooting below
- **Error Handling**: If fails, respond: "I'm unable to process that request right now. Please try again."

**Agent Builder Configuration for this Action:**

1. **Agent Action Instructions**:
   ```
   Call the Mobius AskMe service with the user's question and conversation context. The service will analyze the question and return a detailed answer based on the knowledge base.
   ```

2. **Loading Text**:
   ```
   Searching knowledge base for your answer...
   ```

3. **Input Mapping Instructions**:
   - **userQuery** → Map to `{user_question}` variable
   - **conversation** → Map to `{conversation_context}` variable (from Action 1 output)

4. **Output Mapping Instructions**:
   - **answer** → Map to `mobius_answer` variable (this is what gets shown to the user)

**Troubleshooting - Schema Error with JSON Objects:**

If you get an error like "This Apex class isn't supported. Select a different one", the issue is that the OpenAPI schema has complex JSON object types that Agentforce can't handle directly.

**Solution:** Create a wrapper Apex class to simplify the response:

```apex
public class AskMeWrapper {
    @InvocableMethod(label='Call AskMe Service' description='Calls the Mobius AskMe endpoint and handles complex JSON response')
    public static List<AskMeResponse> callAskMe(List<AskMeRequest> requests) {
        List<AskMeResponse> responses = new List<AskMeResponse>();
        
        for (AskMeRequest req : requests) {
            AskMeResponse resp = new AskMeResponse();
            
            try {
                // Build the request
                HttpRequest httpReq = new HttpRequest();
                httpReq.setEndpoint('https://your-render-app.onrender.com/askme');
                httpReq.setMethod('POST');
                httpReq.setHeader('Content-Type', 'application/json');
                
                // Add Basic Auth header
                String auth = req.username + ':' + req.password;
                String encodedAuth = EncodingUtil.base64Encode(Blob.valueOf(auth));
                httpReq.setHeader('Authorization', 'Basic ' + encodedAuth);
                
                // Build request body
                String body = JSON.serialize(new Map<String, String>{
                    'userQuery' => req.userQuery,
                    'conversation' => req.conversation != null ? req.conversation : ''
                });
                httpReq.setBody(body);
                httpReq.setTimeout(30000);
                
                // Make the call
                Http http = new Http();
                HttpResponse httpResp = http.send(httpReq);
                
                // Parse response
                if (httpResp.getStatusCode() == 200) {
                    Map<String, Object> respMap = (Map<String, Object>) JSON.deserializeUntyped(httpResp.getBody());
                    resp.answer = (String) respMap.get('answer');
                    
                    // Extract conversation context from nested structure
                    if (respMap.containsKey('context')) {
                        Map<String, Object> contextMap = (Map<String, Object>) respMap.get('context');
                        if (contextMap.containsKey('conversation')) {
                            resp.conversationContext = (String) contextMap.get('conversation');
                        }
                    }
                    resp.success = true;
                } else {
                    resp.answer = 'Service error: ' + httpResp.getStatusCode();
                    resp.success = false;
                }
            } catch (Exception e) {
                resp.answer = 'Error calling AskMe service: ' + e.getMessage();
                resp.success = false;
            }
            
            responses.add(resp);
        }
        
        return responses;
    }
    
    public class AskMeRequest {
        @InvocableVariable(label='User Question' required=true)
        public String userQuery;
        
        @InvocableVariable(label='Conversation Context' required=false)
        public String conversation;
        
        @InvocableVariable(label='Username' required=true)
        public String username;
        
        @InvocableVariable(label='Password' required=true)
        public String password;
    }
    
    public class AskMeResponse {
        @InvocableVariable(label='Answer')
        public String answer;
        
        @InvocableVariable(label='Conversation Context')
        public String conversationContext;
        
        @InvocableVariable(label='Success')
        public Boolean success;
    }
}
```

Then use this Apex action instead of the API action if you encounter schema errors.

**Action 3: Update Conversation Context**

Store the conversation context for the next request. Now that you have a Reference Action (Action 2), you can use Flow:

- **Action Type**: **Flow**
- **Reference Action**: Select Action 2 (the AskMe API call)
- **Purpose**: Save returned conversation data to the custom object

**Agent Builder Configuration for this Action:**

1. **Agent Action Instructions**:
   ```
   Update the user's conversation context record with the response from the Mobius service. This ensures follow-up questions will have the full conversation history.
   ```

2. **Loading Text**:
   ```
   Saving conversation for next request...
   ```

3. **Input Mapping Instructions**:
   - Map the output from Action 2 (ask_me_response) to the Flow
   - The Flow will extract the conversation data and save it

4. **Output Mapping Instructions**:
   - This action typically doesn't return output
   - But you can map any success/error messages if your Flow produces them

**Flow Implementation** (Create a Flow with these steps):

Flow Type: **Autolaunched Flow** (no triggers)

```
Step 1 - Decision: Check if context record exists
  Decision Name: Check_Context_Exists
  Condition: 
    - Resource: Agent_Conversation_Context__c
    - Filter: WHERE User__c = {$User.Id}
    - If found, take TRUE path; if not found, take FALSE path

Step 2a (TRUE path) - Update existing record:
  Action: Update Record
  Object: Agent_Conversation_Context__c
  Filter: User__c = {$User.Id}
  Fields to Update:
    - Conversation_Data__c = [map the conversation data from Action 2 response]
    - Last_Updated__c = {$Flow.CurrentDateTime}

Step 2b (FALSE path) - Create new record:
  Action: Create Record
  Object: Agent_Conversation_Context__c
  Field Values:
    - User__c = {$User.Id}
    - Conversation_Data__c = [map the conversation data from Action 2 response]
    - Last_Updated__c = {$Flow.CurrentDateTime}
```

---

**Action 4: Send Response to User**

Display the answer. Use **Prompt Template** for a polished response:

- **Action Type**: **Prompt Template** (recommended for better formatting)
- **Purpose**: Format and display the answer to the user

**Agent Builder Configuration for this Action:**

1. **Agent Action Instructions**:
   ```
   Display the answer from the Mobius service to the user in a clear, professional format.
   ```

2. **Loading Text**:
   ```
   Preparing response...
   ```

3. **Input Mapping Instructions**:
   - **user_question** → Map to `{user_question}` variable
   - **mobius_answer** → Map to `{mobius_answer}` variable (from Action 2)

4. **Output Mapping Instructions**:
   - This action displays to the user; no variable mapping needed

**Prompt Template Configuration**:
```
You are responding to a user's financial question.
The user asked: {user_question}
The Mobius service provided this answer:

{mobius_answer}

Present this answer clearly and professionally to the user.
Do not modify or add to the answer - present it as provided.
```

Or use a simpler version without Prompt Template:
```
{mobius_answer}
```

---- **Or use a simple API response if Prompt Template is not available**:
  - Just display: `{mobius_answer}`

### 10.3 Complete Topic Flow Diagram

```
User asks question
        ↓
Agent analyzes question (is it about banking/finance?)
        ↓
   YES → Trigger "Financial Query Handler" topic
        ↓
   Action 1: Get stored conversation context
        ↓
   Action 2: Call /askme with user question + context
        ↓
   Action 3: Store returned conversation context
        ↓
   Action 4: Display answer to user
        ↓
User sees response and can ask follow-up question
        ↓
On next question, conversation context is retrieved (Action 1) and used again
```

### 10.4 Example User Conversation

```
User: "What was my account balance last month?"

Agent Flow:
1. Recognizes "account balance" as financial query
2. Loads conversation context (empty on first call)
3. Calls AskMe: userQuery="What was my account balance last month?" 
               conversation=""
4. Receives: { "answer": "Your balance on last month...", 
              "context": { "conversation": "user_asked_about_balance..." }}
5. Stores context for future use
6. Shows: "Your balance on last month was..."

---

User: "Can you break that down by month?"

Agent Flow:
1. Recognizes "break down" + financial context
2. Loads stored conversation context: "user_asked_about_balance..."
3. Calls AskMe: userQuery="Can you break that down by month?"
               conversation="user_asked_about_balance..."
4. Mobius uses context to understand "that" refers to previous balance
5. Receives: { "answer": "Month by month breakdown...", 
              "context": { "conversation": "previous_context + new_data..." }}
6. Updates stored context
7. Shows: "Month by month breakdown is..."
```

### 10.5 Implementation Tips

**Maintaining Context Across Sessions:**
- The `Agent_Conversation_Context` object stores context at the user level
- Each user's context is separate and secure
- Conversation context is a string (JSON-formatted) from Mobius
- Don't need to parse it - just pass it back on the next request

**Error Handling:**
- If `/askme` fails, catch the error and notify user
- Don't update context if the request failed
- Optionally log failures to a custom object for debugging

**Testing the Agent:**
1. Open Agent in Preview mode
2. Ask a banking-related question: "What's my account balance?"
3. Verify the answer appears correctly
4. Ask a follow-up: "Show me the past 3 months"
5. Check that context is properly used in the follow-up

**Conversation Context Cleanup:**
- Add a scheduled flow or batch process to delete old context records
- Suggested: Delete records not updated in the last 30 days
- Or clear context when user closes conversation

### 10.6 Security Considerations

- ✅ Store conversation context in Salesforce (encrypted at rest)
- ✅ Use field-level security to restrict who can view context
- ✅ Ensure Mobius credentials are sent via Basic Auth (not stored)
- ✅ Log all requests to `/askme` for audit compliance
- ✅ Clear conversation context on logout or after timeout
- ⚠️ **Important**: Ensure user can only see their own conversation context
- ⚠️ **Important**: Validate that Mobius respects user permissions when returning data

### 10.7 Advanced: Using Apex for Complex Context Management

If you need more sophisticated context handling, create a custom Apex action:

```apex
public class AskMeContextManager {
    public static Map<String, Object> manageContext(String userId, String newContext) {
        // Get existing context
        Agent_Conversation_Context__c contextRecord = [
            SELECT Conversation_Data__c 
            FROM Agent_Conversation_Context__c 
            WHERE User__c = :userId 
            LIMIT 1
        ];
        
        // Update or create
        if (contextRecord != null) {
            contextRecord.Conversation_Data__c = newContext;
            contextRecord.Last_Updated__c = DateTime.now();
            update contextRecord;
        } else {
            contextRecord = new Agent_Conversation_Context__c(
                User__c = userId,
                Conversation_Data__c = newContext,
                Last_Updated__c = DateTime.now()
            );
            insert contextRecord;
        }
        
        return new Map<String, Object>{
            'success' => true,
            'contextId' => contextRecord.Id
        };
    }
}
```

## Step 11: Next Steps and Enhancements

### 11.1 Immediate Improvements
1. **Add more banking data** to make demos more realistic
2. **Implement proper error handling** in your MCP server
3. **Add logging** to track usage and debug issues
4. **Create user documentation** for end users

### 11.2 Advanced Features
1. **Multi-language support** for international customers
2. **Voice integration** for hands-free banking assistance
3. **Transaction processing** for actually modifying services
4. **Integration with core banking systems** for real-time data

### 11.3 Enterprise Integration
1. **SSO integration** for secure user authentication
2. **Audit logging** for compliance requirements
3. **Role-based access control** for different user types
4. **Integration with existing customer service workflows**

## Support and Resources

### Documentation Links
- [Salesforce AgentForce Documentation](https://help.salesforce.com/s/articleView?id=sf.agentforce.htm)
- [External Services Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_external_services.htm)
- [Named Credentials Setup](https://help.salesforce.com/s/articleView?id=sf.named_credentials_about.htm)

### Community Resources
- [Salesforce Developer Forums](https://developer.salesforce.com/forums)
- [AgentForce Trailhead Modules](https://trailhead.salesforce.com/search?keywords=agentforce)
- [Salesforce Stack Exchange](https://salesforce.stackexchange.com/)

### Getting Help
- Check debug logs first
- Test components independently  
- Use Salesforce Developer Support for complex issues
- Join Salesforce Developer Community groups

Remember to keep your documentation updated as Salesforce continues to evolve the AgentForce platform!
