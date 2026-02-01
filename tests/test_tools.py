"""Tests for searchconsole_mcp.tools — all Google API calls are mocked."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from searchconsole_mcp.tools import (
    _get_service,
    list_sites,
    list_sitemaps,
    query_search_analytics,
)


@pytest.fixture()
def mock_service():
    """Patch _get_service to return a mock Google API service."""
    svc = MagicMock()
    with patch("searchconsole_mcp.tools._get_service", return_value=svc):
        yield svc


# ---------------------------------------------------------------------------
# _get_service
# ---------------------------------------------------------------------------


@patch("searchconsole_mcp.tools.build")
@patch("searchconsole_mcp.tools.google.auth.default")
def test_get_service_uses_correct_scope_and_api(mock_auth, mock_build):
    creds = MagicMock()
    mock_auth.return_value = (creds, "project-id")
    mock_build.return_value = MagicMock()

    _get_service()

    mock_auth.assert_called_once_with(
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    creds.refresh.assert_called_once()
    mock_build.assert_called_once_with("searchconsole", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# list_sites
# ---------------------------------------------------------------------------


def test_list_sites_returns_formatted_entries(mock_service):
    mock_service.sites().list().execute.return_value = {
        "siteEntry": [
            {"siteUrl": "https://example.com", "permissionLevel": "siteOwner"},
            {"siteUrl": "sc-domain:example.org", "permissionLevel": "siteFullUser"},
        ]
    }

    result = list_sites()

    assert "https://example.com" in result
    assert "siteOwner" in result
    assert "sc-domain:example.org" in result
    assert "siteFullUser" in result


def test_list_sites_empty(mock_service):
    mock_service.sites().list().execute.return_value = {"siteEntry": []}
    assert list_sites() == "No sites found."


def test_list_sites_missing_key(mock_service):
    mock_service.sites().list().execute.return_value = {}
    assert list_sites() == "No sites found."


# ---------------------------------------------------------------------------
# query_search_analytics
# ---------------------------------------------------------------------------


SAMPLE_ROWS = {
    "rows": [
        {"keys": ["keto recipes"], "clicks": 120, "impressions": 5000, "ctr": 0.024, "position": 8.3},
        {"keys": ["easy meals"], "clicks": 80, "impressions": 3000, "ctr": 0.0267, "position": 12.1},
    ]
}


def test_query_search_analytics_returns_markdown_table(mock_service):
    mock_service.searchanalytics().query().execute.return_value = SAMPLE_ROWS

    result = query_search_analytics("https://example.com", "2025-01-01", "2025-01-07")

    assert "| Query |" in result
    assert "| keto recipes |" in result
    assert "120" in result
    assert "2.40%" in result
    assert "8.3" in result
    assert "Returned 2 rows" in result


def test_query_search_analytics_empty(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {"rows": []}
    result = query_search_analytics("https://example.com", "2025-01-01", "2025-01-07")
    assert result == "No data found for the given query."


def test_query_search_analytics_no_rows_key(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {}
    result = query_search_analytics("https://example.com", "2025-01-01", "2025-01-07")
    assert result == "No data found for the given query."


def test_query_search_analytics_default_dimensions(mock_service):
    mock_service.searchanalytics().query().execute.return_value = SAMPLE_ROWS

    query_search_analytics("https://example.com", "2025-01-01", "2025-01-07")

    call_args = mock_service.searchanalytics().query.call_args
    body = call_args[1]["body"] if "body" in call_args[1] else call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("body")
    assert body["dimensions"] == ["query"]


def test_query_search_analytics_custom_dimensions(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {
        "rows": [{"keys": ["us", "/page"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 5.0}]
    }

    result = query_search_analytics(
        "https://example.com", "2025-01-01", "2025-01-07", dimensions=["country", "page"]
    )

    assert "| Country | Page |" in result
    assert "| us | /page |" in result


def test_query_search_analytics_row_limit_clamped(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {"rows": []}

    # Over max
    query_search_analytics("https://example.com", "2025-01-01", "2025-01-07", row_limit=99999)
    body = mock_service.searchanalytics().query.call_args[1]["body"]
    assert body["rowLimit"] == 25000

    # Under min
    query_search_analytics("https://example.com", "2025-01-01", "2025-01-07", row_limit=-5)
    body = mock_service.searchanalytics().query.call_args[1]["body"]
    assert body["rowLimit"] == 1


def test_query_search_analytics_dimension_filters(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {"rows": []}

    query_search_analytics(
        "https://example.com",
        "2025-01-01",
        "2025-01-07",
        dimension_filters=[{"dimension": "query", "operator": "contains", "expression": "keto"}],
    )

    body = mock_service.searchanalytics().query.call_args[1]["body"]
    assert "dimensionFilterGroups" in body
    filters = body["dimensionFilterGroups"][0]["filters"]
    assert filters[0]["dimension"] == "query"
    assert filters[0]["expression"] == "keto"


def test_query_search_analytics_aggregation_type(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {"rows": []}

    query_search_analytics(
        "https://example.com", "2025-01-01", "2025-01-07", aggregation_type="byPage"
    )

    body = mock_service.searchanalytics().query.call_args[1]["body"]
    assert body["aggregationType"] == "byPage"


def test_query_search_analytics_no_aggregation_type(mock_service):
    mock_service.searchanalytics().query().execute.return_value = {"rows": []}

    query_search_analytics("https://example.com", "2025-01-01", "2025-01-07")

    body = mock_service.searchanalytics().query.call_args[1]["body"]
    assert "aggregationType" not in body


# ---------------------------------------------------------------------------
# list_sitemaps
# ---------------------------------------------------------------------------


def test_list_sitemaps_returns_formatted_entries(mock_service):
    mock_service.sitemaps().list().execute.return_value = {
        "sitemap": [
            {
                "path": "https://example.com/sitemap.xml",
                "lastSubmitted": "2025-01-15T10:00:00Z",
                "isPending": False,
                "warnings": "0",
                "errors": "0",
            }
        ]
    }

    result = list_sitemaps("https://example.com")

    assert "sitemap.xml" in result
    assert "2025-01-15" in result
    assert "Pending: False" in result


def test_list_sitemaps_empty(mock_service):
    mock_service.sitemaps().list().execute.return_value = {"sitemap": []}
    assert list_sitemaps("https://example.com") == "No sitemaps found."


def test_list_sitemaps_missing_key(mock_service):
    mock_service.sitemaps().list().execute.return_value = {}
    assert list_sitemaps("https://example.com") == "No sitemaps found."
