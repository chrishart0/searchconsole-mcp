"""Google Search Console MCP tool definitions."""

from __future__ import annotations

import google.auth
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def _get_service():
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    credentials.refresh(Request())
    return build("searchconsole", "v1", credentials=credentials)


def list_sites() -> str:
    """Lists all verified properties in Google Search Console.

    Returns site URLs and permission levels.
    """
    service = _get_service()
    response = service.sites().list().execute()
    sites = response.get("siteEntry", [])
    if not sites:
        return "No sites found."
    lines = []
    for site in sites:
        lines.append(
            f"- {site['siteUrl']} (permission: {site.get('permissionLevel', 'unknown')})"
        )
    return "\n".join(lines)


def query_search_analytics(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str] | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
    dimension_filters: list[dict] | None = None,
    search_type: str = "web",
    aggregation_type: str | None = None,
) -> str:
    """Query Google Search Console search analytics data.

    This is the main keyword research tool. Returns rows with clicks,
    impressions, CTR, and average position.

    Args:
        site_url: The site URL as it appears in Search Console
            (e.g. "https://mychefai.com" or "sc-domain:mychefai.com").
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        dimensions: List of dimensions to group by. Options: query, page,
            date, country, device, searchAppearance. Defaults to ["query"].
        row_limit: Max rows to return (1-25000, default 1000).
        start_row: Starting row offset for pagination (default 0).
        dimension_filters: Optional list of filter objects. Each filter has:
            - dimension: the dimension to filter on (e.g. "query", "page")
            - operator: one of "contains", "equals", "notContains",
              "notEquals", "includingRegex", "excludingRegex"
            - expression: the filter value
            Example: [{"dimension": "query", "operator": "contains",
                        "expression": "keto"}]
        search_type: Type of search results. One of: web, image, video,
            news, discover, googleNews. Default "web".
        aggregation_type: How to aggregate results. One of: auto, byPage,
            byProperty. If omitted, the API auto-selects.
    """
    service = _get_service()

    if dimensions is None:
        dimensions = ["query"]

    body: dict = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": min(max(row_limit, 1), 25000),
        "startRow": start_row,
        "type": search_type,
    }

    if aggregation_type:
        body["aggregationType"] = aggregation_type

    if dimension_filters:
        body["dimensionFilterGroups"] = [
            {
                "filters": [
                    {
                        "dimension": f["dimension"],
                        "operator": f.get("operator", "contains"),
                        "expression": f["expression"],
                    }
                    for f in dimension_filters
                ]
            }
        ]

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=body)
        .execute()
    )

    rows = response.get("rows", [])
    if not rows:
        return "No data found for the given query."

    lines = [
        f"Returned {len(rows)} rows "
        f"(startRow={start_row}, rowLimit={body['rowLimit']}).",
        "",
    ]

    # Header
    dim_headers = " | ".join(d.capitalize() for d in dimensions)
    lines.append(f"| {dim_headers} | Clicks | Impressions | CTR | Position |")
    lines.append(
        f"| {'--- | ' * len(dimensions)}--- | --- | --- | --- |"
    )

    for row in rows:
        keys = row.get("keys", [])
        keys_str = " | ".join(keys)
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = f"{row.get('ctr', 0):.2%}"
        position = f"{row.get('position', 0):.1f}"
        lines.append(
            f"| {keys_str} | {clicks} | {impressions} | {ctr} | {position} |"
        )

    return "\n".join(lines)


def list_sitemaps(site_url: str) -> str:
    """Lists submitted sitemaps for a Search Console property.

    Args:
        site_url: The site URL as it appears in Search Console
            (e.g. "https://mychefai.com" or "sc-domain:mychefai.com").
    """
    service = _get_service()
    response = service.sitemaps().list(siteUrl=site_url).execute()
    sitemaps = response.get("sitemap", [])
    if not sitemaps:
        return "No sitemaps found."
    lines = []
    for sm in sitemaps:
        path = sm.get("path", "unknown")
        last_submitted = sm.get("lastSubmitted", "unknown")
        is_pending = sm.get("isPending", False)
        warnings_count = sm.get("warnings", "0")
        errors_count = sm.get("errors", "0")
        lines.append(
            f"- {path}\n"
            f"  Last submitted: {last_submitted}\n"
            f"  Pending: {is_pending} | Warnings: {warnings_count} | Errors: {errors_count}"
        )
    return "\n".join(lines)
