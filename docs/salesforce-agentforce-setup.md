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

## Step 10: Next Steps and Enhancements

### 10.1 Immediate Improvements
1. **Add more banking data** to make demos more realistic
2. **Implement proper error handling** in your MCP server
3. **Add logging** to track usage and debug issues
4. **Create user documentation** for end users

### 10.2 Advanced Features
1. **Multi-language support** for international customers
2. **Voice integration** for hands-free banking assistance
3. **Transaction processing** for actually modifying services
4. **Integration with core banking systems** for real-time data

### 10.3 Enterprise Integration
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
