"""Google Search Console MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from searchconsole_mcp.tools import list_sitemaps, list_sites, query_search_analytics

mcp = FastMCP("searchconsole-mcp")

mcp.tool()(list_sites)
mcp.tool()(query_search_analytics)
mcp.tool()(list_sitemaps)


def run_server():
    mcp.run()


if __name__ == "__main__":
    run_server()
