# AgentForce + MCP Server Demo Guide

## Demo Overview

This demo showcases how Salesforce AgentForce can integrate with an HTTP-deployed MCP server to provide intelligent banking service assistance. The demo highlights:

- **Real-time external data integration** via HTTP REST API
- **Conversational AI** that understands banking terminology
- **Dynamic parameter mapping** from natural language to API calls
- **Professional customer service responses** with contextual follow-ups

## Demo Setup (5 minutes before demo)

### Pre-Demo Checklist
- [ ] Verify MCP server is running: `https://your-render-app.onrender.com/health`
- [ ] Test External Service: Setup → External Services → ContentMCPService → Test
- [ ] Confirm agent is active: Setup → Agentforce Agents → Banking Content Assistant
- [ ] Have demo script ready with sample customer IDs

### Quick Test
Run this test to ensure everything works:
```
Agent Preview → "Show me autopayments for customer C123"
Expected: Returns Verizon $79.99 payment
```

## Demo Script (10-15 minutes)

### 1. Introduction (2 minutes)
**"Today I'll show you how we've integrated Salesforce AgentForce with our banking systems using the Model Context Protocol to create an intelligent banking assistant."**

**Key Points:**
- AgentForce provides conversational AI interface
- MCP server contains real banking data (standing instructions, autopayments, service links)
- Integration allows real-time data access through natural language

### 2. Architecture Overview (2 minutes)
**Show the flow diagram:**
```
Customer Question → AgentForce → External Service → HTTP MCP Server → Banking Data
                ←             ←                  ←                ←
```

**Explain:**
- "Customer asks natural language questions"
- "AgentForce interprets intent and extracts parameters"
- "External Service calls our HTTP MCP server with structured data"
- "MCP server searches banking data and returns results"
- "AgentForce presents results in customer-friendly language"

### 3. Live Demo - Basic Searches (4 minutes)

**Where to navigate for the demo:**
1. **Go to Salesforce Setup**: Your-org-url.lightning.force.com/lightning/setup/SetupOneHome/home
2. **Navigate to Agentforce Agents**: Setup → Quick Find → "Agentforce Agents"
3. **Open your agent**: Click on "Banking Content Assistant" 
4. **Open Builder**: Click the **"Open in Builder"** button
5. **Find Preview**: Once in Agent Builder, look for **"Preview"** button (usually top-right area)
6. **Demo Interface**: This opens the conversational interface where you type questions

**Alternative Navigation:**
- **App Launcher method**: Click 9-dots → Search "Agentforce" → Click "Agentforce Agents" → "Banking Content Assistant" → "Open in Builder" → "Preview"
- **Direct URL**: `https://your-org.lightning.force.com/lightning/setup/AgentforceAgents/home` → Select your agent → "Open in Builder" → "Preview"

**Navigation Flow:**
```
Agentforce Agents List → Banking Content Assistant → "Open in Builder" → Agent Builder Interface → "Preview" Button → Chat Interface
```

**If you still don't see Preview:**
- Make sure your agent is **Active** (should show "Active" status)
- Look for **"Test"** or **"Try it"** button as alternative names
- Try refreshing the Agent Builder page
- Check if Preview is in a dropdown menu or under "More Actions"

**Demo 1: Simple Autopayment Search**
**Type in the message box:**
```
Show me autopayments for customer C123
```
**Expected Response:** "I found 1 autopayment for customer C123: $79.99 to Verizon on the 15th monthly from Credit ****4242. Would you like me to search for other types of services or help you with anything else?"

**Demo 2: Comprehensive Service Search**
**Type in the message box:**
```
Find all services for customer C123
```
**Expected Response:** Lists all 3 services (autopayment, standing instruction, service link)

**Demo 3: Specific Service Type**
**Type in the message box:**
```
What standing instructions exist for customer C123?
```
**Expected Response:** "$500 monthly transfer from Checking ****1234 to Mortgage ****5678"

### 4. Advanced Capabilities (3 minutes)

**Demo 4: Status Filtering**
```
Input: "Show me closed services for customer C456"
Expected Response: "Closed Roth IRA at Delta Funds (transferred out 2024-12-31)"
```

**Demo 5: No Results Handling**
```
Input: "Find services for customer C999"
Expected Response: Professional "no results found" with helpful suggestions
```

**Demo 6: Missing Information**
```
Input: "Show me all autopayments"
Expected Response: Agent asks for customer ID for security
```

### 5. Technical Highlights (2 minutes)

**Show behind the scenes (open in separate tabs beforehand):**

**Tab 1: External Service Configuration**
- **URL**: `https://your-org.lightning.force.com/lightning/setup/ExternalServices/home`
- **Navigate**: Setup → Integrations → External Services → ContentMCPService
- **Show**: The connection to your MCP server, test functionality

**Tab 2: Agent Builder Configuration**  
- **URL**: `https://your-org.lightning.force.com/lightning/setup/AgentforceAgents/home`
- **Navigate**: Setup → Agentforce Agents → Banking Content Assistant → Edit
- **Show**: Topics tab, Actions configuration, how natural language maps to API calls

**Tab 3: MCP Server API (optional)**
- **URL**: `https://your-render-app.onrender.com/`
- **Show**: The test interface, API health check, raw JSON responses

**Tab 4: Live API Call (advanced demo)**
- **URL**: `https://your-render-app.onrender.com/api/v1/actions/search_content`
- **Tool**: Use browser dev tools or Postman to show raw API call
- **Payload**: 
```json
{
  "classes": "autopayment",
  "customer_id": "C123"
}
```

### 6. Business Value (2 minutes)

**Key Benefits:**
- **Reduced training time**: Natural language interface vs complex banking systems
- **Consistent responses**: Standardized information access
- **Real-time data**: Always current service information
- **Scalable architecture**: Easy to add new data sources
- **Compliance ready**: Audit trails and secure access

### 7. End User Access - How Your Team Will Use This (3 minutes)

**"Now let me show you how your customer service representatives and banking staff would actually use this in their daily work."**

**Option 1: Service Cloud Console Integration**

**⚠️ Setup Required First (do this before demo):**

1. **Enable Service Cloud Console:**
   - Setup → App Manager → New Lightning App
   - Choose "Console Navigation"
   - App Name: "Banking Service Console"
   - Add tabs: Cases, Accounts, Contacts, Banking Agent Assistant

2. **Add Agent to Console (Method 1 - Lightning Page):**
   - Setup → Lightning App Builder → New → App Page
   - Choose "Utility Bar" template
   - Drag "AgentForce Agent" component to utility bar
   - Select your "Banking Content Assistant" agent
   - Save and activate for the Banking Service Console

3. **Add Agent to Console (Method 2 - Custom Component):**
   - In Service Console → Settings (gear icon) → Edit Page
   - Add "Lightning Component" to sidebar
   - Configure to show AgentForce interface

**Alternative Demo Approach if Console isn't configured:**
- **Navigate**: App Launcher → Banking Agent Assistant (your custom app)
- **Explain**: "In production, this would appear as a sidebar in the Service Console"
- **Show**: The agent interface as a dedicated tab
- **Demonstrate**: How reps would switch between customer records and the agent

**Demo Script for Service Console:**
```
"Let me show you how a customer service rep would use this during a call:

1. Customer calls: 'Hi, I want to check my autopayments'
2. Rep opens customer record in Service Console  
3. Rep clicks the Banking Assistant in the utility bar
4. Rep types: 'Show autopayments for customer C123'
5. Agent responds with payment details instantly
6. Rep can immediately help customer without switching systems"
```

**Option 2: Lightning App Tab (Easier Demo)**  
- **Navigate**: App Launcher → Banking Agent Assistant (the custom app you created in Step 5.6)
- **Show**: Dedicated workspace for banking queries
- **Explain**: "Staff can access this directly when they need to lookup customer services"
- **Demo**: This is the easiest way to show the agent working

**If Banking Agent Assistant app doesn't exist, create it quickly:**
```
Setup → App Manager → New Lightning App
- App Name: Banking Agent Assistant  
- Add Tab: Your AgentForce agent (if available as tab)
- Or create custom tab pointing to agent URL
```

## Demo Variations by Audience

### For Technical Teams
**Focus on:**
- MCP protocol implementation
- External Service configuration
- Error handling and debugging
- Performance and scalability
- Security considerations

**Show:**
- Code structure in `content_mcp_server.py`
- OpenAPI schema generation
- Debug logs in Salesforce
- Render deployment dashboard

### For Business Users
**Focus on:**
- Customer experience improvements
- Reduced call handling time
- Consistent service quality
- Easy access to complex banking data

**Show:**
- Customer-facing conversation flow
- Professional response formatting
- Multiple service type handling
- Helpful follow-up suggestions

### For Executives
**Focus on:**
- Strategic technology integration
- Customer satisfaction improvements
- Operational efficiency gains
- Future expansion possibilities

**Metrics to mention:**
- Reduced average call time
- Improved first-call resolution
- Decreased training requirements
- Increased agent productivity

### For End User Managers
**Focus on:**
- How their team will use it daily
- Training requirements (minimal)
- User adoption strategy
- Productivity improvements
- Customer satisfaction impact

**Show:**
- Service Console integration
- Simple conversation examples
- Permission and security controls
- Reporting and usage analytics

## Common Demo Questions & Answers

### Q: "How secure is this integration?"
**A:** "The integration uses Salesforce's built-in External Service security with Named Credentials. In production, we add API key authentication, rate limiting, and audit logging. All data stays within our controlled environment."

### Q: "What if the external service is down?"
**A:** "AgentForce handles this gracefully - the agent explains there's a temporary issue and offers alternative assistance. We also have monitoring and alerting in place."

### Q: "How hard is it to add new data sources?"
**A:** "Very easy - we just add new endpoints to our MCP server and configure new actions in AgentForce. The conversational interface stays the same for users."

### Q: "Can this handle more complex banking scenarios?"
**A:** "Absolutely. This is a simple demo, but the architecture supports transaction processing, account management, regulatory compliance, and integration with core banking systems."

### Q: "What about different languages or regions?"
**A:** "AgentForce supports multiple languages natively, and our MCP server can be configured for regional banking regulations and local terminology."

### Q: "How will our customer service reps learn to use this?"
**A:** "The beauty is there's almost no learning curve - they just ask questions in plain English. We provide a 15-minute orientation on banking terminology, and they're ready to go. Compare that to weeks of training on complex banking systems."

### Q: "Can customers use this directly?"
**A:** "Yes, we can deploy it in your customer portal for self-service. The agent automatically verifies customer identity before showing any sensitive information. This reduces call volume for simple inquiries."

### Q: "What if a rep asks something the agent can't answer?"
**A:** "The agent gracefully explains what it can't do and suggests alternatives, like escalating to a specialist or accessing different systems. It's designed to enhance, not replace, human expertise."

### Q: "How do we control who has access?"
**A:** "Through Salesforce's standard permission system. We can give different access levels - some users might only see certain service types, others get full access. Everything is auditable for compliance."

## Technical Deep Dive (Optional)

### Show the MCP Server Code
```python
# Quick walkthrough of key components:
# 1. Data model (ContentItem class)
# 2. Search logic (call_tool method)
# 3. HTTP endpoints for Salesforce
# 4. Response formatting
```

### Show Salesforce Configuration
- Named Credentials setup
- External Service schema
- Agent Builder topic configuration
- Action parameter mapping

### Show Integration Flow
- Live API call demonstration
- Parameter transformation
- Response parsing
- Agent response generation

## Demo Troubleshooting

### If Demo Breaks:

**Agent doesn't respond:**
1. Check if agent is still active
2. Verify MCP server is running (`/health` endpoint)
3. Use External Service test function
4. Fall back to manual API demonstration

**Wrong responses:**
1. Check topic action configuration
2. Verify parameter mapping
3. Test MCP server directly
4. Show debug logs if available

**Server issues:**
1. Have backup Render deployment ready
2. Show local development version
3. Use recorded demo video as backup
4. Focus on architecture explanation

**Can't find Preview button:**
1. Ensure agent is Active (not Draft status)
2. Look for "Test", "Try it", or "Chat" buttons as alternatives
3. Try refreshing the Agent Builder page
4. Check if it's in a dropdown menu
5. **Fallback**: Use External Service Test function in Setup → External Services → ContentMCPService → Test

**Can't find agent in Service Console:**
1. **Quick Fix**: Use Lightning App instead
   - App Launcher → Banking Agent Assistant
   - Explain this would normally be embedded in Service Console
2. **For future demos**: Set up Console integration beforehand
3. **Fallback**: Show agent through Setup → AgentForce Agents → Preview

**No Banking Agent Assistant app:**
1. Create quickly: Setup → App Manager → New Lightning App
2. Add any relevant tabs (Cases, Accounts, etc.)
3. Use as standalone agent workspace
4. Or just demonstrate through AgentForce Agents → Preview

## Follow-up Materials

### Leave-behinds:
- Architecture diagram
- Setup documentation link
- Contact information for technical questions
- Timeline for production implementation

### Next Steps Discussion:
- Production deployment requirements
- Additional data source integration
- Custom banking scenarios
- Performance and scaling considerations
- Security and compliance requirements

## Demo Success Metrics

**Immediate feedback:**
- Audience engagement during demo
- Technical questions asked
- Business value recognition
- Interest in next steps

**Follow-up actions:**
- Request for detailed documentation
- Technical deep-dive meetings scheduled
- Pilot project discussions
- Integration planning sessions

---

**Remember:** Keep the demo conversational and interactive. Encourage questions and adapt the technical depth based on your audience's expertise level.
