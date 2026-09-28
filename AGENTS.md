# AGENTS.md

Guide for coding agents (Claude Code, Codex, etc.) and human contributors working in this repo.

## What this is

An MCP (Model Context Protocol) server for the Semantic Scholar academic paper API — six tools for
searching papers, tracing citations/references, and looking up authors. No API key required for
basic use; a free personal key raises rate limits. Single-package Python project.

## How to navigate it

- `src/semantic_scholar_mcp/server.py` — tool definitions (`search_papers`, `get_paper`,
  `get_citations`, `get_references`, `get_author`, `search_by_field`).
- `src/semantic_scholar_mcp/client.py` — the Semantic Scholar HTTP client: request building, rate
  limiting, and retry-on-429 logic. Changes to API behavior belong here, not in `server.py`.
- `src/semantic_scholar_mcp/__init__.py` — package entry point.
- `pyproject.toml` — dependencies (`mcp[cli]`, `httpx`) and the `semantic-scholar-mcp` console script.
- `README.md` — install instructions, tool table, paper-ID formats, and rate-limit notes; keep it in
  sync with any new tool or client behavior.

## Build, test, lint

```bash
uv sync                                              # install deps into .venv
uv run python -c "import semantic_scholar_mcp.server"   # quick import/smoke check
uv run semantic-scholar-mcp                          # run the server (stdio transport)
```

There is no automated test suite or linter configured yet. Given `client.py` has retry/rate-limit
logic that's easy to break silently, adding `pytest` coverage for it (as a `dev` optional-dependency
group) is worth doing before it grows further.

## Standards this repo owns

- All outbound Semantic Scholar calls go through `client.py`, including retry/backoff handling —
  don't add a second HTTP call path in `server.py`.
- Accept all three paper-ID formats (Semantic Scholar ID, `DOI:`, `ARXIV:`) anywhere a `paper_id`
  is taken; document new formats in the README table if you add one.
- Any new tool must be documented in the `README.md` tools table in the same change.

## PR, review, and commit rules

- Branch → PR → full `/code-review` before merge.
- Merge commits, not squash.
- No `Co-Authored-By` or other AI-attribution lines in commits.
- Secrets (a personal `SEMANTIC_SCHOLAR_API_KEY`, if used) live only in `.env` or the consumer's
  MCP config, never committed.

Keep this file and the README current when structure or commands change.
