<div align="center">

# SwanLab MCP Server

[![][github-shield]][github-shield-link]  &nbsp; [![][pypi-version-shield]][pypi-version-shield-link]  &nbsp; [![][license-shield]][license-shield-link]


</div>


> SwanLab-MCP-Server 是一个基于 Python 的 MCP（Model Context Protocol）服务器实现，基于 SwanLab OpenAPI HTTP 接口层（SwanLab SDK >= 0.9.0）与 FastMCP 3 框架构建。

## ✨ 功能特性

### 核心功能

- **用户与空间查询** - 获取当前认证用户信息与工作空间元数据
- **项目查询** - 分页列出空间下项目（支持搜索/排序），获取单个项目详情
- **实验查询** - 分页与结构化条件筛选实验列表，获取实验详情、配置、元数据与依赖
- **指标键发现** - 列出实验的指标键名（标量/媒体、自定义/系统监控，支持模糊搜索）
- **指标查询** - 标量指标（支持采样与范围查询）、统计摘要、媒体数据与控制台日志
- **API 集成** - 直接调用 SwanLab OpenAPI 原始端点（纯 JSON 响应、真实后端错误信息）；数据量大的指标查询复用 SDK 下载机制

### 技术栈

- **语言**: Python 3.12+
- **核心框架**: FastMCP (>= 3.4.7)
- **API 客户端**: SwanLab SDK (>= 0.9.0)
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

> **说明**：如果已经通过 `swanlab login` 登录，可以不设置 `SWANLAB_API_KEY`，服务器会自动使用 `~/.swanlab/.netrc` 中保存的凭证；也可以通过 `SWANLAB_HOST` 指向其他 SwanLab 实例。

### 环境要求

- Python >= 3.12
- SwanLab API Key（从 [SwanLab](https://swanlab.cn) 获取），或本地的 `swanlab login` 登录态

### 安装

```bash
# 使用 uv 安装（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 配置

#### 环境变量

创建 `.env` 文件并配置 API 密钥（若已 `swanlab login` 可省略）：

```bash
cp .env.template .env
```

编辑 `.env` 文件：

```env
SWANLAB_API_KEY=your_api_key_here
# SWANLAB_HOST=https://swanlab.cn   # 可选，指向其他 SwanLab 实例
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
- `swanlab_get_user` - 获取当前认证用户信息
- `swanlab_list_workspaces` - 列出用户可访问的工作空间
- `swanlab_get_workspace` - 获取工作空间详情
- `swanlab_list_projects` - 分页列出空间下的项目（支持搜索/排序）
- `swanlab_get_project` - 获取项目详情
- `swanlab_list_runs` - 分页列出项目中的实验
- `swanlab_filter_runs` - 结构化条件筛选实验（state / `config.*` / 指标值）
- `swanlab_get_run` - 获取实验详情（含 profile）
- `swanlab_get_run_config` - 获取实验配置（超参数）
- `swanlab_get_run_metadata` - 获取实验环境元信息（Python 版本、硬件等）
- `swanlab_get_run_requirements` - 获取实验 Python 依赖
- `swanlab_list_run_series` - 列出实验的指标键名（标量/媒体、自定义/系统，支持模糊搜索）
- `swanlab_get_run_metrics` - 获取标量指标数据（支持采样、全量导出与范围查询）
- `swanlab_get_run_summary` - 获取标量指标统计摘要（min/max/avg/median/stdDev）
- `swanlab_get_run_medias` - 获取媒体指标数据（图片/音频/文本，含下载 URL）
- `swanlab_get_run_logs` - 获取实验运行期间的控制台日志
- `swanlab_export_run_logs` - 导出控制台日志为 `.log` 文件（返回下载 URL）

资源定义：
- **workspace**：项目集合，对应研发空间（`PERSON`/`TEAM`），唯一标识 `username`。
- **project**：实验集合，唯一标识 `path = username/project_name`。
- **run**：单次实验，唯一标识 `path = username/project_name/run_id`。
- **series**：实验的指标键，按 `metric_type`（SCALAR/MEDIA）与 `metric_class`（CUSTOM/SYSTEM）过滤。
- **metric**：每个指标的数据点与统计值，统一返回 `{path, keys, sample, series, total}`。

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
- [FastMCP](https://github.com/jlowin/fastmcp)
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

