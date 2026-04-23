"""HTTP client for the Semantic Scholar API."""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx

BASE_URL = "https://api.semanticscholar.org/graph/v1"
USER_AGENT = "semantic-scholar-mcp/0.1.0 (https://github.com/harshanchenna/mcp-semantic-scholar)"
_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")

# Simple token-bucket rate limiter: 100 req/min = ~1.67 req/s without API key.
# We cap at 90 req/min to leave a safety margin.
_RATE_LIMIT = 90  # requests per minute
_MIN_INTERVAL = 60.0 / _RATE_LIMIT  # seconds between requests
_last_request_time: float = 0.0
_lock = asyncio.Lock()


async def _throttle() -> None:
    """Ensure we don't exceed the rate limit."""
    global _last_request_time
    async with _lock:
        now = time.monotonic()
        elapsed = now - _last_request_time
        if elapsed < _MIN_INTERVAL:
            await asyncio.sleep(_MIN_INTERVAL - elapsed)
        _last_request_time = time.monotonic()


def _make_client() -> httpx.AsyncClient:
    headers: dict[str, str] = {"User-Agent": USER_AGENT}
    if _API_KEY:
        headers["x-api-key"] = _API_KEY
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers=headers,
        timeout=30.0,
    )


async def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Perform a GET request with rate limiting and basic error handling."""
    await _throttle()
    async with _make_client() as client:
        response = await client.get(path, params=params)
        if response.status_code == 429:
            # Back off and retry once
            retry_after = int(response.headers.get("Retry-After", "10"))
            await asyncio.sleep(retry_after)
            await _throttle()
            async with _make_client() as retry_client:
                response = await retry_client.get(path, params=params)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Paper search
# ---------------------------------------------------------------------------

async def search_papers(
    query: str,
    limit: int = 10,
    fields: str = "title,abstract,year,citationCount,authors,url,externalIds",
) -> dict[str, Any]:
    return await _get("/paper/search", params={"query": query, "limit": limit, "fields": fields})


async def search_papers_by_field(
    query: str,
    field_of_study: str,
    limit: int = 10,
    fields: str = "title,abstract,year,citationCount,authors,url,externalIds",
) -> dict[str, Any]:
    return await _get(
        "/paper/search",
        params={
            "query": query,
            "fieldsOfStudy": field_of_study,
            "limit": limit,
            "fields": fields,
        },
    )


# ---------------------------------------------------------------------------
# Single paper
# ---------------------------------------------------------------------------

async def get_paper(
    paper_id: str,
    fields: str = "title,abstract,year,citationCount,referenceCount,authors,url,externalIds,tldr",
) -> dict[str, Any]:
    return await _get(f"/paper/{paper_id}", params={"fields": fields})


async def get_citations(
    paper_id: str,
    limit: int = 10,
    fields: str = "title,year,citationCount,authors,url",
) -> dict[str, Any]:
    return await _get(
        f"/paper/{paper_id}/citations",
        params={"limit": limit, "fields": fields},
    )


async def get_references(
    paper_id: str,
    limit: int = 10,
    fields: str = "title,year,citationCount,authors,url",
) -> dict[str, Any]:
    return await _get(
        f"/paper/{paper_id}/references",
        params={"limit": limit, "fields": fields},
    )


# ---------------------------------------------------------------------------
# Author
# ---------------------------------------------------------------------------

async def get_author(
    author_id: str,
    fields: str = "name,hIndex,paperCount,citationCount,url",
) -> dict[str, Any]:
    return await _get(f"/author/{author_id}", params={"fields": fields})


async def get_author_papers(
    author_id: str,
    limit: int = 10,
    fields: str = "title,year,citationCount,url",
) -> dict[str, Any]:
    return await _get(
        f"/author/{author_id}/papers",
        params={"limit": limit, "fields": fields},
    )
