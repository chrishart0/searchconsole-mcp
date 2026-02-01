# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server providing read-only access to Google Search Console data. Built with FastMCP, Python 3.11+, and the Google API client.

## Commands

```bash
# Install dependencies
uv sync

# Run the server
searchconsole-mcp

# Build the package
uv build

# Add a dependency
uv add <package>
```

## Architecture

The codebase is small (~186 lines) with a clear separation:

- **`searchconsole_mcp/server.py`** — FastMCP server setup. Creates the `mcp` instance, registers the three tools, and exports `run_server()` as the CLI entry point.
- **`searchconsole_mcp/tools.py`** — All tool implementations. Contains `_get_service()` (builds the Google API client using Application Default Credentials with `webmasters.readonly` scope) and three tools: `list_sites`, `query_search_analytics`, `list_sitemaps`.

The server communicates over stdio. Each tool call creates a fresh Google API service instance via `_get_service()`. Tools return plain text or markdown tables.

## Authentication

Uses Google Application Default Credentials (`google.auth.default()`). The environment must have valid Google Cloud credentials configured (service account, user credentials, or `GOOGLE_APPLICATION_CREDENTIALS` env var).

## Git Conventions

The default branch is `master`, not `main`. Use `master` for PRs and branch references.
