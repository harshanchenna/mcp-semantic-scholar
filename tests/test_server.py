"""Smoke tests: the server imports, exposes its tools, and formats output
without making any network calls (no credentials required)."""

from __future__ import annotations

import asyncio

import pytest

from semantic_scholar_mcp import server
from semantic_scholar_mcp.server import _external_ids, _fmt_authors, _fmt_paper_summary

EXPECTED_TOOLS = {
    "search_papers",
    "get_paper",
    "get_citations",
    "get_references",
    "get_author",
    "search_by_field",
}


def test_all_tools_are_registered() -> None:
    tools = asyncio.run(server.mcp.list_tools())
    names = {t.name for t in tools}
    assert EXPECTED_TOOLS <= names


def test_fmt_authors_empty() -> None:
    assert _fmt_authors([]) == "Unknown"


def test_fmt_authors_few() -> None:
    authors = [{"name": "A"}, {"name": "B"}]
    assert _fmt_authors(authors) == "A, B"


def test_fmt_authors_truncates_long_lists() -> None:
    authors = [{"name": f"Author{i}"} for i in range(5)]
    result = _fmt_authors(authors)
    assert result.startswith("Author0, Author1")
    assert "more" in result


def test_fmt_paper_summary_handles_missing_fields() -> None:
    summary = _fmt_paper_summary({})
    assert "No title" in summary
    assert "Citations: 0" in summary


def test_external_ids_none() -> None:
    assert _external_ids(None) == ""


def test_external_ids_doi_and_arxiv() -> None:
    result = _external_ids({"DOI": "10.1/x", "ArXiv": "1234.5678"})
    assert "DOI:10.1/x" in result
    assert "ARXIV:1234.5678" in result


def test_main_entry_point_exists() -> None:
    assert callable(server.main)
