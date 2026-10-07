# mcp-semantic-scholar

<!-- mcp-name: io.github.harshanchenna/mcp-semantic-scholar -->

MCP server for the [Semantic Scholar](https://www.semanticscholar.org/) academic paper search API. Search 200M+ papers, trace citations and references, and look up author profiles — all from Claude or any MCP-compatible client.

## Quick start

```bash
uvx --from harshanchenna-mcp-semantic-scholar semantic-scholar-mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `search_papers` | Full-text search across all Semantic Scholar papers |
| `get_paper` | Full details for a paper by Semantic Scholar ID, DOI, or ArXiv ID |
| `get_citations` | Papers that cite a given paper |
| `get_references` | Papers referenced by a given paper |
| `get_author` | Author profile with h-index, citation count, and top papers |
| `search_by_field` | Search constrained to a specific academic field of study |

## Paper ID formats

All tools that accept a `paper_id` support three formats:

| Format | Example |
|--------|---------|
| Semantic Scholar ID | `649def34f8be52c8b66281af98ae884c09aef38b` |
| DOI | `DOI:10.18653/v1/N18-3011` |
| ArXiv | `ARXIV:1706.03762` |

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install with uv

```bash
git clone https://github.com/harshanchenna/mcp-semantic-scholar.git
cd mcp-semantic-scholar
uv sync
```

### Add to Claude Code (published package)

```bash
claude mcp add semantic-scholar -- uvx --from harshanchenna-mcp-semantic-scholar semantic-scholar-mcp
```

### Add to Claude Desktop (published package)

```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "uvx",
      "args": ["--from", "harshanchenna-mcp-semantic-scholar", "semantic-scholar-mcp"]
    }
  }
}
```

### Add to Claude Code (from a local clone)

After cloning, register the server with Claude Code. Replace `/path/to/mcp-semantic-scholar` with your actual clone path:

```bash
claude mcp add semantic-scholar -- uv run --project /path/to/mcp-semantic-scholar semantic-scholar-mcp
```

Or if you prefer the `--with-editable` form:

```bash
claude mcp add semantic-scholar -- uv run --with-editable /path/to/mcp-semantic-scholar semantic-scholar-mcp
```

### Add to Claude Desktop (from a local clone)

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "uv",
      "args": [
        "run",
        "--project", "/path/to/mcp-semantic-scholar",
        "semantic-scholar-mcp"
      ]
    }
  }
}
```

## Usage examples

**Search for papers on a topic:**
> "Search for recent papers on mechanistic interpretability of transformers"

**Get full details for a specific paper:**
> "Get details for ARXIV:1706.03762" (Attention Is All You Need)

**Trace who cited a paper:**
> "Show me papers that cite DOI:10.48550/arXiv.2303.08774"

**Look up an author:**
> "Find papers by author ID 1741101"

**Search within a field:**
> "Search for papers on protein folding in the Biology field"

## API key and rate limits

The Semantic Scholar API is free and requires no API key for basic usage.

| Mode | Rate limit | Throttle |
|------|-----------|---------|
| No API key | ~100 req/min | Server throttles to 90 req/min |
| Personal API key | Higher limits | Throttle adjusts automatically |

The server handles rate limiting and retries automatically on 429 responses. To use a personal API key (available free at [Semantic Scholar](https://www.semanticscholar.org/product/api)), set the environment variable before starting the server:

```bash
export SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

## License

MIT — see [LICENSE](LICENSE).
