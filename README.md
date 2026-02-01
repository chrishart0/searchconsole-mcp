# searchconsole-mcp

MCP (Model Context Protocol) server providing read-only access to Google Search Console data.

## Tools

| Tool | Description |
|------|-------------|
| `list_sites` | Lists all verified properties with permission levels |
| `query_search_analytics` | Query keyword data — clicks, impressions, CTR, position |
| `list_sitemaps` | Lists submitted sitemaps for a property |

## Setup

### Install

```bash
uv sync
```

### Authentication

Uses [Google Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials). Set up one of:

- **Service account key:** `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
- **User credentials:** `gcloud auth application-default login --scopes="https://www.googleapis.com/auth/webmasters.readonly"`

The service account or user must have access to the Search Console properties.

### Claude Code integration

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

## Development

```bash
uv sync --dev
uv run pytest
```
