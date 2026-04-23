"""FastMCP server exposing Semantic Scholar API tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import client as ss

mcp = FastMCP(
    "semantic-scholar",
    instructions=(
        "Search and retrieve academic papers from Semantic Scholar. "
        "Use paper IDs in Semantic Scholar format (e.g. '649def34f8be52c8b66281af98ae884c09aef38b'), "
        "DOI prefixed with 'DOI:', or ArXiv IDs prefixed with 'ARXIV:' (e.g. 'ARXIV:2303.08774')."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_authors(authors: list[dict[str, Any]]) -> str:
    names = [a.get("name", "") for a in (authors or [])]
    if not names:
        return "Unknown"
    if len(names) <= 3:
        return ", ".join(names)
    return f"{names[0]}, {names[1]}, … +{len(names) - 2} more"


def _fmt_paper_summary(paper: dict[str, Any]) -> str:
    """One-line paper summary."""
    title = paper.get("title") or "No title"
    year = paper.get("year") or "?"
    citations = paper.get("citationCount", 0)
    authors = _fmt_authors(paper.get("authors", []))
    url = paper.get("url") or ""
    return f"[{year}] {title}\n  Authors: {authors}\n  Citations: {citations}\n  URL: {url}"


def _external_ids(ids: dict[str, Any] | None) -> str:
    if not ids:
        return ""
    parts = []
    if ids.get("DOI"):
        parts.append(f"DOI:{ids['DOI']}")
    if ids.get("ArXiv"):
        parts.append(f"ARXIV:{ids['ArXiv']}")
    return "  IDs: " + ", ".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def search_papers(query: str, limit: int = 10) -> str:
    """Search Semantic Scholar for academic papers matching a query.

    Args:
        query: Search terms (e.g. 'attention is all you need', 'RLHF language models').
        limit: Number of results to return (1-50, default 10).
    """
    limit = max(1, min(50, limit))
    try:
        data = await ss.search_papers(query, limit=limit)
    except Exception as exc:
        return f"Error searching papers: {exc}"

    papers = data.get("data") or []
    total = data.get("total", len(papers))

    if not papers:
        return f"No papers found for query: {query!r}"

    lines = [f"Found {total} papers (showing {len(papers)}):\n"]
    for i, p in enumerate(papers, 1):
        lines.append(f"{i}. {_fmt_paper_summary(p)}")
        ext = _external_ids(p.get("externalIds"))
        if ext:
            lines.append(ext)
        abstract = (p.get("abstract") or "").strip()
        if abstract:
            snippet = abstract[:200] + ("…" if len(abstract) > 200 else "")
            lines.append(f"  Abstract: {snippet}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_paper(paper_id: str) -> str:
    """Get full details for a specific paper.

    Args:
        paper_id: Semantic Scholar paper ID, DOI (prefix with 'DOI:'), or ArXiv ID
                  (prefix with 'ARXIV:'). Example: 'ARXIV:1706.03762' or 'DOI:10.48550/arXiv.1706.03762'.
    """
    try:
        p = await ss.get_paper(paper_id)
    except Exception as exc:
        return f"Error fetching paper {paper_id!r}: {exc}"

    title = p.get("title") or "No title"
    year = p.get("year") or "?"
    citations = p.get("citationCount", 0)
    references = p.get("referenceCount", 0)
    authors = _fmt_authors(p.get("authors", []))
    url = p.get("url") or ""
    abstract = (p.get("abstract") or "No abstract available.").strip()
    tldr_obj = p.get("tldr") or {}
    tldr = tldr_obj.get("text") if isinstance(tldr_obj, dict) else None
    ext = _external_ids(p.get("externalIds"))

    lines = [
        f"Title: {title}",
        f"Year: {year}",
        f"Authors: {authors}",
        f"Citations: {citations}  |  References: {references}",
        f"URL: {url}",
    ]
    if ext:
        lines.append(ext.strip())
    if tldr:
        lines.append(f"\nTL;DR: {tldr}")
    lines.append(f"\nAbstract:\n{abstract}")

    return "\n".join(lines)


@mcp.tool()
async def get_citations(paper_id: str, limit: int = 10) -> str:
    """Get papers that cite a given paper.

    Args:
        paper_id: Semantic Scholar paper ID, or prefixed DOI/ArXiv ID.
        limit: Number of citing papers to return (1-50, default 10).
    """
    limit = max(1, min(50, limit))
    try:
        data = await ss.get_citations(paper_id, limit=limit)
    except Exception as exc:
        return f"Error fetching citations for {paper_id!r}: {exc}"

    items = data.get("data") or []
    if not items:
        return f"No citations found for paper {paper_id!r}."

    lines = [f"Papers citing {paper_id} (showing {len(items)}):\n"]
    for i, item in enumerate(items, 1):
        citing = item.get("citingPaper") or item  # API wraps in citingPaper
        lines.append(f"{i}. {_fmt_paper_summary(citing)}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_references(paper_id: str, limit: int = 10) -> str:
    """Get papers referenced by a given paper.

    Args:
        paper_id: Semantic Scholar paper ID, or prefixed DOI/ArXiv ID.
        limit: Number of references to return (1-50, default 10).
    """
    limit = max(1, min(50, limit))
    try:
        data = await ss.get_references(paper_id, limit=limit)
    except Exception as exc:
        return f"Error fetching references for {paper_id!r}: {exc}"

    items = data.get("data") or []
    if not items:
        return f"No references found for paper {paper_id!r}."

    lines = [f"References in {paper_id} (showing {len(items)}):\n"]
    for i, item in enumerate(items, 1):
        cited = item.get("citedPaper") or item  # API wraps in citedPaper
        lines.append(f"{i}. {_fmt_paper_summary(cited)}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
async def get_author(author_id: str, include_papers: bool = True) -> str:
    """Get information about an author and their top papers.

    Args:
        author_id: Semantic Scholar author ID (numeric, e.g. '1741101').
        include_papers: Whether to include a list of top papers (default True).
    """
    try:
        author = await ss.get_author(author_id)
    except Exception as exc:
        return f"Error fetching author {author_id!r}: {exc}"

    name = author.get("name") or "Unknown"
    h_index = author.get("hIndex", "N/A")
    paper_count = author.get("paperCount", "N/A")
    citation_count = author.get("citationCount", "N/A")
    url = author.get("url") or ""

    lines = [
        f"Author: {name}",
        f"h-index: {h_index}",
        f"Papers: {paper_count}  |  Total citations: {citation_count}",
        f"URL: {url}",
    ]

    if include_papers:
        try:
            papers_data = await ss.get_author_papers(author_id, limit=10)
            papers = papers_data.get("data") or []
            if papers:
                lines.append("\nTop papers:")
                for i, p in enumerate(papers, 1):
                    lines.append(f"  {i}. {_fmt_paper_summary(p)}")
        except Exception as exc:
            lines.append(f"\n(Could not fetch papers: {exc})")

    return "\n".join(lines)


@mcp.tool()
async def search_by_field(query: str, field_of_study: str, limit: int = 10) -> str:
    """Search for papers within a specific academic field of study.

    Args:
        query: Search terms.
        field_of_study: Field name, e.g. 'Computer Science', 'Medicine', 'Physics',
                        'Mathematics', 'Biology', 'Chemistry', 'Economics',
                        'Engineering', 'AI Safety', 'Neuroscience'.
        limit: Number of results to return (1-50, default 10).
    """
    limit = max(1, min(50, limit))
    try:
        data = await ss.search_papers_by_field(query, field_of_study=field_of_study, limit=limit)
    except Exception as exc:
        return f"Error searching papers in field {field_of_study!r}: {exc}"

    papers = data.get("data") or []
    total = data.get("total", len(papers))

    if not papers:
        return f"No papers found for query {query!r} in field {field_of_study!r}."

    lines = [f"Found {total} papers in '{field_of_study}' (showing {len(papers)}):\n"]
    for i, p in enumerate(papers, 1):
        lines.append(f"{i}. {_fmt_paper_summary(p)}")
        ext = _external_ids(p.get("externalIds"))
        if ext:
            lines.append(ext)
        abstract = (p.get("abstract") or "").strip()
        if abstract:
            snippet = abstract[:200] + ("…" if len(abstract) > 200 else "")
            lines.append(f"  Abstract: {snippet}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
