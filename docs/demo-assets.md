# Demo Assets and Backup Plans

## Quick Demo Script (2-minute version)

### For Elevator Pitch:
1. **"Watch this"** - Open AgentForce Preview
2. **"Natural language query"** - Type: "Show me autopayments for customer C123"
3. **"Real-time external data"** - Show the Verizon payment result
4. **"Business value"** - "Customer service reps can now access complex banking data through simple conversation"

## Demo Screenshots

### Capture these screens beforehand:
1. **Agent Builder Overview** - Shows topics and actions configured
2. **External Service Configuration** - Shows MCP server connection
3. **Successful Test Result** - External Service test with good response
4. **Agent Preview Interface** - Clean conversation interface
5. **Sample Conversation** - Good example of agent response
6. **MCP Server Health Check** - Shows server is running
7. **Architecture Diagram** - Flow from user to data

## Backup Demo Options

### Option 1: Pre-recorded Video
Record a successful demo session showing:
- Agent responding to various queries
- Different customer scenarios
- Professional response formatting
- Error handling gracefully

### Option 2: Local Development Demo
If cloud services fail:
- Run MCP server locally with `python content_mcp_server.py`
- Use ngrok for public endpoint: `ngrok http 10000`
- Update Named Credential to ngrok URL
- Proceed with normal demo

### Option 3: Static API Demo
Show the integration without AgentForce:
- Use Postman or curl to call MCP server directly
- Show request/response format
- Explain how AgentForce would use this data
- Discuss the conversational layer benefits

## Demo Data Explanation

### Customer Scenarios:
- **C123**: Full-service customer (has all 3 service types)
- **C456**: Customer with closed services (shows historical data)
- **C789**: Simple customer (only autopayments)
- **C999**: Non-existent customer (shows error handling)

### Service Types:
- **Standing Instructions**: Recurring transfers between accounts
- **Autopayments**: Scheduled payments to external companies
- **Service Links**: Connected external financial services

## Audience-Specific Talking Points

### For IT Directors:
- "Reduces integration complexity between systems"
- "Standard protocols for future expansion"
- "Built on Salesforce security model"
- "Scales with existing infrastructure"

### For Customer Service Managers:
- "Reduces training time for new agents"
- "Consistent information across all interactions"
- "Faster resolution of customer queries"
- "Professional response formatting"

### For Business Analysts:
- "Bridge between technical systems and business needs"
- "Configurable for different business scenarios"
- "Audit trail for compliance requirements"
- "Measurable improvements in service metrics"

## Common Objections & Responses

### "This seems too complex for our team"
**Response:** "The complexity is hidden - users just have natural conversations. The technical setup is one-time, and we provide full documentation and training."

### "What about data security?"
**Response:** "All data stays within your controlled environment. We use Salesforce's enterprise security model with additional authentication layers."

### "How much does this cost?"
**Response:** "The MCP server runs on minimal infrastructure. Main costs are Salesforce licensing you likely already have. ROI comes from reduced training and faster customer service."

### "Will this work with our existing systems?"
**Response:** "Yes - MCP is a standard protocol. We can integrate with any system that has an API or database connection."

## Demo Environment Checklist

### Before Demo Day:
- [ ] Test complete demo flow 24 hours before
- [ ] Have backup internet connection available
- [ ] Prepare demo on multiple devices
- [ ] Create screen recording as backup
- [ ] Print architecture diagrams
- [ ] Prepare business card/contact info
- [ ] Test audio/video if presenting remotely

### During Demo:
- [ ] Close unnecessary browser tabs
- [ ] Disable notifications
- [ ] Have water available
- [ ] Prepare for questions at any time
- [ ] Keep energy high and engaging
- [ ] Watch audience reactions
- [ ] Adapt technical depth as needed

### After Demo:
- [ ] Send follow-up materials immediately
- [ ] Answer any questions that came up
- [ ] Schedule technical deep-dive if requested
- [ ] Provide access to documentation
- [ ] Set up pilot project timeline

## Success Stories to Share

### Example Scenarios:
- **"A major bank reduced customer call time by 40%"** - Agents could access complex account information instantly
- **"Training time cut from 6 weeks to 2 weeks"** - Natural language interface eliminated system complexity
- **"First-call resolution improved 25%"** - Agents had complete information immediately
- **"Customer satisfaction scores increased"** - Faster, more accurate service

Remember: Tailor these examples to your audience's industry and concerns.
