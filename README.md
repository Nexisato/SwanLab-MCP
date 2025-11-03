# SwanLab-MCP-Server

> A Model Context Protocol (MCP) server implementation for SwanLab, combining SwanLab-OpenAPI & FastMCP.

## ✨ Features

### Core Features

- **Workspace Management** - List and manage user-accessible workspaces
- **Project Management** - Create, retrieve, delete projects, and list project information
- **Experiment Management** - Create, retrieve, delete experiments, and retrieve experiment metrics and summaries
- **API Integration** - Provide complete platform access through SwanLab OpenAPI

### Tech Stack

- **Language**: Python 3.12+
- **Core Framework**: FastMCP (v2.14.4+)
- **API Client**: SwanLab SDK
- **Config Management**: Pydantic Settings
- **Logging**: Loguru

## 🚀 Quick Start

### ❗️Configuration

Add the following configuration to your relative mcp config list

```json
{
  "mcpServers": 
    ...
    {
    "swanlab-mcp": {
      "command": "uv",
      "args": ["run", "swanlab_mcp", "--transport", "stdio"],
      "env": {
        "SWANLAB_API_KEY": "your_api_key_here"
      }
    }
  }
}
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

# Using SSE transport
python -m swanlab_mcp --transport sse

# Using HTTP transport
python -m swanlab_mcp --transport http

# Check version
python -m swanlab_mcp --version
```

### Usage

After configuration, restart Claude Desktop to interact with SwanLab via the MCP protocol.

Available Tools:
- `swanlab_list_workspaces` - List workspaces
- `swanlab_create_project` - Create project
- `swanlab_list_projects` - List projects
- `swanlab_create_experiment` - Create experiment
- `swanlab_list_experiments` - List experiments
- `swanlab_get_experiment` - Get experiment details
- `swanlab_delete_experiment` - Delete experiment

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