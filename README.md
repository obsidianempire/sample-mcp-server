# Sample MCP Server with Salesforce AgentForce Integration

A Model Context Protocol (MCP) server designed for integration with Salesforce AgentForce to provide intelligent banking service assistance. The server supports both HTTP REST API mode (for Salesforce) and MCP protocol mode (for compatible clients).

## Features

- **Salesforce AgentForce Integration**: External Service compatible HTTP endpoints
- **Banking Data Search**: Standing instructions, autopayments, and service links
- **Natural Language Queries**: AgentForce converts conversation to structured data
- **Web Test Interface**: Built-in testing and debugging tools
- **MCP Protocol Support**: Compatible with MCP clients when needed

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Salesforce Developer Edition org (for AgentForce integration)
- Render account (for cloud deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sample-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run as HTTP server** (for Salesforce integration):
   ```bash
   MCP_SERVER_MODE=http PORT=10000 python src/content_mcp_server.py
   ```
   Then visit: http://localhost:10000 (this is also the default mode when `MCP_SERVER_MODE` is not set)

4. **Run as MCP server** (for MCP clients only):
   ```bash
   MCP_SERVER_MODE=mcp python src/content_mcp_server.py
   ```
   Install the optional MCP dependency when using this mode:
   ```bash
   pip install fastmcp
   ```
   Set the `MCP_TRANSPORT` environment variable to switch between transports (defaults to `sse`):
   ```bash
   MCP_SERVER_MODE=mcp MCP_TRANSPORT=http python src/content_mcp_server.py  # HTTP transport
   MCP_SERVER_MODE=mcp MCP_TRANSPORT=sse python src/content_mcp_server.py   # Server-sent events
   ```

### Cloud Deployment (Render)

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/content_mcp_server.py`
   - Environment Variables:
     - `PORT=10000`
     - `MCP_SERVER_MODE=http` (default HTTP/REST mode for Salesforce)
4. **Optional – MCP mode instead of HTTP**:
   - Add `fastmcp` to your dependencies (e.g., `pip install fastmcp` during build or include it in `requirements.txt`)
   - Change the environment variable to `MCP_SERVER_MODE=mcp`
   - (Recommended) set `MCP_TRANSPORT=sse` unless your MCP client expects HTTP transport
4. **Deploy and get your public URL**

### Salesforce AgentForce Setup

Follow the comprehensive setup guide: [docs/salesforce-agentforce-setup.md](docs/salesforce-agentforce-setup.md)

**Quick setup summary**:
1. Create Named Credential pointing to your Render URL
2. Create External Service using `/api/v1/actions` endpoint
3. Create AgentForce agent with banking assistant template
4. Add topics and link to External Service actions
5. Test with sample queries

## API Endpoints

### HTTP REST API (Primary Usage)

- `GET /health` - Health check
- `GET /` - Interactive test interface
- `POST /tools/call` - MCP-style tool calling
- `GET /tools/list` - List available tools

### Salesforce External Service Endpoints

- `GET /api/v1/actions` - OpenAPI schema for External Service registration
- `POST /api/v1/actions/search_content` - Main search endpoint for AgentForce
- `GET /api/v1/content` - REST-style search (GET parameters)
- `POST /api/v1/content/search` - REST-style search (POST body)
- `GET /api/health` - Service health for monitoring

### MCP Protocol (Optional)
Standard MCP JSON-RPC over stdin/stdout when run without PORT environment variable (for MCP client compatibility).

## Sample Data

The server includes sample banking data for demonstration:

- **Customer C123**: 3 services (autopayment, standing instruction, service link)
- **Customer C456**: 1 closed service (Roth IRA)
- **Customer C789**: 1 autopayment (GymPro)

### Service Types

- **standing_instruction**: Recurring transfers between accounts
- **autopayment**: Scheduled payments to external companies
- **service_link**: Connected external financial services

## Usage Examples

### Test Queries for AgentForce

```
"Show me autopayments for customer C123"
"Find all services for customer C123"
"What standing instructions exist for customer C123?"
"Show me closed services for customer C456"
"Find services for customer C999" (no results)
```

### Direct API Calls

```bash
# Test the search endpoint
curl -X POST https://your-app.onrender.com/api/v1/actions/search_content \
  -H "Content-Type: application/json" \
  -d '{"classes": "autopayment", "customer_id": "C123"}'

# Health check
curl https://your-app.onrender.com/health
```

## Project Structure

```
sample-mcp-server/
├── src/
│   └── content_mcp_server.py    # Main server (MCP + HTTP)
├── docs/
│   ├── salesforce-agentforce-setup.md  # Complete setup guide
│   ├── demo-guide.md                   # Demo instructions
│   └── demo-assets.md                  # Demo support materials
├── requirements.txt             # Python dependencies
├── render.yaml                 # Render deployment config
└── README.md                  # This file
```

## Architecture

```
Customer Query → AgentForce → External Service → MCP Server → Banking Data
              ←             ←                  ←            ←
```

1. **Customer asks natural language questions in AgentForce**
2. **AgentForce interprets intent and extracts parameters**
3. **External Service calls MCP server via HTTP with structured data**
4. **MCP server searches banking data and returns results**
5. **AgentForce presents results in customer-friendly language**

## Development

### Testing

- **HTTP testing**: Use the built-in web interface at `/`
- **Salesforce testing**: Use External Service test function
- **AgentForce testing**: Use Preview mode in Agent Builder
- **MCP client testing**: Use Claude Desktop or compatible MCP client (optional)

## Demo Instructions

See [docs/demo-guide.md](docs/demo-guide.md) for complete demo instructions including:
- Setup checklist
- Demo script with sample queries
- Troubleshooting common issues
- Audience-specific variations

## Troubleshooting

### Common Issues

1. **Agent doesn't respond**:
   - Check if agent is active in Salesforce
   - Verify MCP server is running (`/health` endpoint)
   - Test External Service independently

2. **External Service not found**:
   - Ensure Named Credential is configured correctly
   - Verify External Service points to correct URL
   - Check OpenAPI schema is valid

3. **Wrong responses**:
   - Verify topic action configuration in AgentForce
   - Check parameter mapping in action setup
   - Test MCP server directly with curl

### Debug Mode

Enable debug logging by setting environment variables:
```bash
DEBUG=true python src/content_mcp_server.py
```

## Production Considerations

### Security
- Add API key authentication for production
- Implement rate limiting
- Use HTTPS for all external communications
- Audit log all banking data access

### Performance
- Add caching for frequently accessed data
- Implement connection pooling for databases
- Monitor response times and set up alerting
- Scale horizontally with load balancers

### Compliance
- Implement proper audit trails
- Add data retention policies
- Ensure GDPR/privacy compliance
- Regular security assessments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Complete setup guide in [docs/](docs/) folder
- **Demo Support**: Use [docs/demo-guide.md](docs/demo-guide.md) for presentations

## Related Links

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Salesforce AgentForce Documentation](https://help.salesforce.com/s/articleView?id=sf.agentforce.htm)
- [External Services Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_external_services.htm)
