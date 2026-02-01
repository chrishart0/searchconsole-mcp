# searchconsole-mcp

[![CI](https://github.com/chrishart0/searchconsole-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/chrishart0/searchconsole-mcp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [MCP](https://modelcontextprotocol.io/) server that gives AI assistants read-only access to your Google Search Console data. Ask questions about your site's search performance in natural language — keywords, clicks, impressions, CTR, rankings, sitemaps, and more.

## Tools

| Tool | Description |
|------|-------------|
| `list_sites` | Lists all verified Search Console properties with permission levels |
| `query_search_analytics` | Query keyword/page data — clicks, impressions, CTR, average position. Supports filtering by dimension, date range, search type, and pagination |
| `list_sitemaps` | Lists submitted sitemaps for a property |

## Quick Start

### 1. Install

```bash
git clone https://github.com/chrishart0/searchconsole-mcp.git
cd searchconsole-mcp
uv sync
```

### 2. Authenticate

This server uses [Google Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials). Choose one:

**Option A — Service account key** (recommended for automation):
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Option B — User credentials** (recommended for local development):
```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/webmasters.readonly"
```

The service account or user must have access to the Search Console properties you want to query.

### 3. Connect to your MCP client

<details>
<summary><strong>Claude Code</strong></summary>

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "searchconsole-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/searchconsole-mcp", "searchconsole-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "searchconsole-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/searchconsole-mcp", "searchconsole-mcp"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/key.json"
      }
    }
  }
}
```

</details>

<details>
<summary><strong>Other MCP clients</strong></summary>

Any MCP-compatible client can connect over stdio. Run the server with:

```bash
uv run --directory /path/to/searchconsole-mcp searchconsole-mcp
```

</details>

## Example Prompts

Once connected, try asking your AI assistant:

- "What are my top 10 keywords by clicks this month?"
- "Show me pages with high impressions but low CTR"
- "List all my Search Console properties"
- "What queries is my site ranking for on page 2 of Google?"
- "Show me my sitemaps and their status"

## Development

```bash
uv sync --dev
uv run pytest
```

## License

[MIT](LICENSE)
