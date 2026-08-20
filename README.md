<div align="center">

# SwanLab MCP Server

[![][github-shield]][github-shield-link] &nbsp;  &nbsp; [![][pypi-version-shield]][pypi-version-shield-link] &nbsp;  &nbsp; [![][license-shield]][license-shield-link]

</div>


> A Model Context Protocol (MCP) server implementation for SwanLab, built on the SwanLab OpenAPI HTTP layer (SwanLab SDK >= 0.9.0) & FastMCP 3.

## ✨ Features

### Core Features

- **User & Workspace Queries** - Inspect the authenticated user and workspace metadata
- **Project Queries** - Paginated project lists with search/sort, plus single project details
- **Run Queries** - Paginated and structured-filter run lists, run details, config, metadata and requirements
- **Series Discovery** - List metric keys (scalar/media, custom/system) with fuzzy search
- **Metric Queries** - Scalar metrics with sampling and range queries, summaries, medias and console logs
- **API Integration** - Read-only access via the raw SwanLab OpenAPI endpoints (plain JSON, real backend error messages); data-heavy metric queries reuse the SDK download machinery

### Tech Stack

- **Language**: Python 3.12+
- **Core Framework**: FastMCP (>= 3.4.7)
- **API Client**: SwanLab SDK (>= 0.9.0)
- **Config Management**: Pydantic Settings

## 🚀 Quick Start

### ❗️Configuration

Add the following configuration to your relative mcp config list

```json
{
  "mcpServers": 
    ...
    {
    "swanlab-mcp": {
      "command": "uvx",
      "args": ["--from", "swanlab-mcp", "swanlab_mcp", "--transport", "stdio"],
      "env": {
        "SWANLAB_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

For `Claude Code` Users, you can config like this:

```bash
claude mcp add --env SWANLAB_API_KEY=<your_api_key> -- swanlab_mcp uvx --from swanlab-mcp swanlab_mcp --transport stdio
```

> **Note**: `SWANLAB_API_KEY` is optional if you have already logged in with `swanlab login` — the server falls back to the credentials stored in `~/.swanlab/.netrc`. You can also set `SWANLAB_HOST` to target another SwanLab instance.

### Prerequisites

- Python >= 3.12
- SwanLab API Key (get it from [SwanLab](https://swanlab.cn)), or a local `swanlab login` session

### Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Configuration

#### Environment Variables

Create a `.env` file and configure your API key (optional if logged in via `swanlab login`):

```bash
cp .env.template .env
```

Edit the `.env` file:

```env
SWANLAB_API_KEY=your_api_key_here
# SWANLAB_HOST=https://swanlab.cn   # optional, target another SwanLab instance
```

### Running

```bash
# Using stdio transport (default)
python -m swanlab_mcp

# Or using CLI
python -m swanlab_mcp --transport stdio

# Check version
python -m swanlab_mcp --version
```

### Usage

After configuration, restart Claude Desktop to interact with SwanLab via the MCP protocol.

Available Tools:
- `swanlab_get_user` - Get the authenticated user's profile
- `swanlab_list_workspaces` - List workspaces accessible to a user
- `swanlab_get_workspace` - Get workspace details
- `swanlab_list_projects` - List projects under a workspace (paginated, with search/sort)
- `swanlab_get_project` - Get project details
- `swanlab_list_runs` - List runs in a project (paginated)
- `swanlab_filter_runs` - Filter runs with a structured query (state / `config.*` / metric values)
- `swanlab_get_run` - Get run details (including profile)
- `swanlab_get_run_config` - Get run config (hyperparameters)
- `swanlab_get_run_metadata` - Get run metadata (Python version, hardware, etc.)
- `swanlab_get_run_requirements` - Get run Python requirements
- `swanlab_list_run_series` - List metric keys of a run (scalar/media, custom/system, fuzzy search)
- `swanlab_get_run_metrics` - Get scalar metric data (sampling, full export, range queries)
- `swanlab_get_run_summary` - Get scalar metric statistics (min/max/avg/median/stdDev)
- `swanlab_get_run_medias` - Get media metric data (images/audio/text with URLs)
- `swanlab_get_run_logs` - Get console logs captured during a run
- `swanlab_export_run_logs` - Export console logs as a downloadable `.log` file

Resource Definitions:
- **workspace**: collection of projects (`PERSON` or `TEAM`) identified by `username`.
- **project**: collection of runs identified by `path = username/project_name`.
- **run**: single experiment identified by `path = username/project_name/run_id`.
- **series**: metric keys of a run, filtered by `metric_type` (SCALAR/MEDIA) and `metric_class` (CUSTOM/SYSTEM).
- **metric**: per-key data points and statistics, returned as `{path, keys, sample, series, total}`.

## 🛠️ Development

### Code Formatting

```bash
# Using Makefile
make format

# Or manually
uvx isort . --skip-gitignore
uvx ruff format . --quiet
```

### Lint Check

```bash
uvx ruff check .
```

### Pre-commit Hooks

```bash
bash scripts/install-hooks.sh
```

## 📚 References & Acknowledgements

- [SwanLab](https://github.com/SwanHubX/SwanLab)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [modelscope-mcp-server](https://github.com/modelscope/modelscope-mcp-server)
- [TrackIO-mcp-server](https://github.com/fcakyon/trackio-mcp)
- [Simple-Wandb-mcp-server](https://github.com/tsilva/simple-wandb-mcp-server)

## 📄 License

MIT License

[license-shield]: https://img.shields.io/badge/license-MIT%202.0-e0e0e0?labelColor=black&style=flat-square "License"
[license-shield-link]: https://github.com/Nexisato/SwanLab-MCP/blob/main/LICENSE

[github-shield]: https://img.shields.io/badge/GitHub-black?logo=github&style=flat-square "GitHub"
[github-shield-link]: https://github.com/Nexisato/SwanLab-MCP

[pypi-version-shield]: https://img.shields.io/pypi/v/swanlab-mcp?color=c4f042&labelColor=black&style=flat-square "PyPI"
[pypi-version-shield-link]: https://pypi.org/project/swanlab-mcp/
