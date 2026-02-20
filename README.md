<div align="center">

# SwanLab MCP Server

[![][github-shield]][github-shield-link] &nbsp;  &nbsp; [![][pypi-version-shield]][pypi-version-shield-link] &nbsp;  &nbsp; [![][license-shield]][license-shield-link]

</div>


> A Model Context Protocol (MCP) server implementation for SwanLab, combining SwanLab-OpenAPI & FastMCP.

## ✨ Features

### Core Features

- **Workspace Queries** - List accessible workspaces and enumerate workspace projects
- **Project Queries** - List projects and inspect a specific project with run summaries
- **Run Queries** - Inspect runs with normalized fields (`id`, `state`, `profile`, `user`)
- **Metric Queries** - Fetch metric tables with consistent `columns`, `rows`, and `total`
- **API Integration** - Provide read-only access through SwanLab OpenAPI (`swanlab.Api`)

### Tech Stack

- **Language**: Python 3.12+
- **Core Framework**: FastMCP (v2.14.4+)
- **API Client**: SwanLab SDK
- **Config Management**: Pydantic Settings

## 🚀 Quick Start

### ❗️Configuration

Add the following configuration to your relative mcp config list

```json
{
  "mcpServers": {
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
claude mcp add --env SWANLAB_API_KEY=<your_api_key> -- swanlab-mcp uvx --from swanlab-mcp swanlab_mcp --transport stdio
```

### Prerequisites

- Python >= 3.12
- SwanLab API Key (get it from [SwanLab](https://swanlab.cn))

### Installation

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Configuration

#### Environment Variables

Create a `.env` file and configure your API key:

```bash
cp .env.template .env
```

Edit the `.env` file:

```env
SWANLAB_API_KEY=your_api_key_here
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
- `swanlab_list_workspaces` - List workspaces
- `swanlab_get_workspace` - Get workspace details
- `swanlab_list_projects_in_workspace` - List projects in one workspace
- `swanlab_list_projects` - List projects
- `swanlab_get_project` - Get project details
- `swanlab_list_runs_in_project` - List runs in one project
- `swanlab_list_runs` - List runs with optional filters (`state`, `config.*`)
- `swanlab_get_run` - Get run details
- `swanlab_get_run_config` - Get run config
- `swanlab_get_run_metadata` - Get run metadata
- `swanlab_get_run_requirements` - Get run requirements
- `swanlab_get_run_metrics` - Get run metric table

Resource Definitions:
- **workspace**: collection of projects (`PERSON` or `TEAM`) identified by `username`.
- **project**: collection of runs identified by `path = username/project_name`.
- **run**: single experiment identified by `path = username/project_name/experiment_id`.
- **metric**: tabular run history returned as `{path, keys, x_axis, sample, columns, rows, total}`.

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
- [FastMCP v2](https://github.com/jlowin/fastmcp)
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
