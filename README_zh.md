<div align="center">

# SwanLab MCP Server

[![][github-shield]][github-shield-link]  &nbsp; [![][pypi-version-shield]][pypi-version-shield-link]  &nbsp; [![][license-shield]][license-shield-link]


</div>


> SwanLab-MCP-Server 是一个基于 Python 的 MCP（Model Context Protocol）服务器实现，结合了 SwanLab-OpenAPI 和 FastMCP 框架。

## ✨ 功能特性

### 核心功能

- **工作空间查询** - 列出可访问空间，并查看空间下项目
- **项目查询** - 列出项目并查看指定项目详情与实验列表
- **实验查询** - 统一返回 run 定义（`id`、`state`、`profile`、`user`）
- **指标查询** - 统一返回指标表结构（`columns`、`rows`、`total`）
- **API 集成** - 基于 SwanLab OpenAPI（`swanlab.Api`）提供只读访问

### 技术栈

- **语言**: Python 3.12+
- **核心框架**: FastMCP (v2.14.4+)
- **API 客户端**: SwanLab SDK
- **配置管理**: Pydantic Settings

## 🚀 快速开始


### ❗️重要【配置方式】

在你对应的 mcp 配置文件中赋值如下配置 (如 `cursor`, `claude code`, 或许也可以手动实现？) 

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
对于 `Claude Code` 用户，可以一次性配置：

```bash
claude mcp add --env SWANLAB_API_KEY=<your_api_key> -- swanlab_mcp uvx --from swanlab-mcp swanlab_mcp --transport stdio
```

### 环境要求

- Python >= 3.12
- SwanLab API Key（从 [SwanLab](https://swanlab.cn) 获取）

### 安装

```bash
# 使用 uv 安装（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 配置

#### 环境变量

创建 `.env` 文件并配置 API 密钥：

```bash
cp .env.template .env
```

编辑 `.env` 文件：

```env
SWANLAB_API_KEY=your_api_key_here
```

### 运行

```bash
# 使用 stdio 传输（默认）
python -m swanlab_mcp

# 或使用 CLI
python -m swanlab_mcp --transport stdio

# 查看版本
python -m swanlab_mcp --version
```

### 使用

配置完成后，重启 Claude Desktop，即可通过 MCP 协议与 SwanLab 进行交互。

可用工具：
- `swanlab_list_workspaces` - 列出工作空间
- `swanlab_get_workspace` - 获取工作空间详情
- `swanlab_list_projects_in_workspace` - 列出空间中的项目
- `swanlab_list_projects` - 列出项目
- `swanlab_get_project` - 获取项目详情
- `swanlab_list_runs_in_project` - 列出项目中的实验
- `swanlab_list_runs` - 列出实验（支持 `state`、`config.*` 过滤）
- `swanlab_get_run` - 获取实验详情
- `swanlab_get_run_config` - 获取实验配置
- `swanlab_get_run_metadata` - 获取实验环境元信息
- `swanlab_get_run_requirements` - 获取实验依赖信息
- `swanlab_list_run_metric_keys` - 列出实验可用的指标键名
- `swanlab_get_run_metrics` - 获取实验指标表

资源定义：
- **workspace**：项目集合，对应研发空间（`PERSON`/`TEAM`），唯一标识 `username`。
- **project**：实验集合，唯一标识 `path = username/project_name`。
- **run**：单次实验，唯一标识 `path = username/project_name/experiment_id`。
- **metric**：实验指标时序表，统一返回 `{path, keys, x_axis, sample, columns, rows, total}`。

## 🛠️ 开发

### 代码格式化

```bash
# 使用 Makefile
make format

# 或手动执行
uvx isort . --skip-gitignore
uvx ruff format . --quiet
```

### Lint 检查

```bash
uvx ruff check .
```

### Pre-commit 钩子

```bash
bash scripts/install-hooks.sh
```

## 📚 参考资料

- [SwanLab](https://github.com/SwanHubX/SwanLab)
- [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastMCP v2](https://github.com/jlowin/fastmcp)
- [modelscope-mcp-server](https://github.com/modelscope/modelscope-mcp-server)
- [TrackIO-mcp-server](https://github.com/fcakyon/trackio-mcp)
- [Simple-Wandb-mcp-server](https://github.com/tsilva/simple-wandb-mcp-server)

## 📄 许可证

MIT License



[license-shield]: https://img.shields.io/badge/license-MIT%202.0-e0e0e0?labelColor=black&style=flat-square "License"
[license-shield-link]: https://github.com/Nexisato/SwanLab-MCP/blob/main/LICENSE

[github-shield]: https://img.shields.io/badge/GitHub-black?logo=github&style=flat-square "GitHub"
[github-shield-link]: https://github.com/Nexisato/SwanLab-MCP

[pypi-version-shield]: https://img.shields.io/pypi/v/swanlab-mcp?color=c4f042&labelColor=black&style=flat-square "PyPI"
[pypi-version-shield-link]: https://pypi.org/project/swanlab-mcp/

