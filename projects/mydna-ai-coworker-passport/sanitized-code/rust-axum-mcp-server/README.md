# In-Process Axum MCP Server (Sanitized Reference)

Standalone reference implementation of the local Model Context Protocol (MCP) server listening on port 5050.

## Endpoint
- `GET /mcp/resources/user_dna`: Returns JSON-RPC 2.0 developer context payload.

## Verification
```bash
cargo test
```
