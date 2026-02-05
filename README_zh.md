# SwanLab-MCP-Server

> SwanLab-MCP-Server 是一个基于 Python 的 MCP（Model Context Protocol）服务器实现，结合了 SwanLab-OpenAPI 和 FastMCP 框架。

## ✨ 功能特性

### 核心功能

- **工作空间管理** - 列出和管理用户可访问的工作空间
- **项目管理** - 创建、获取、删除项目，以及列出项目信息
- **实验管理** - 创建、获取、删除实验，检索实验指标和摘要
- **API 集成** - 通过 SwanLab OpenAPI 提供完整的平台访问能力

### 技术栈

- **语言**: Python 3.12+
- **核心框架**: FastMCP (v2.14.4+)
- **API 客户端**: SwanLab SDK
- **配置管理**: Pydantic Settings
- **日志**: Loguru

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
      "args": ["swanlab_mcp", "--transport", "stdio"],
      "env": {
        "SWANLAB_API_KEY": "your_api_key_here"
      }
    }
  }
}
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

# 使用 SSE 传输
python -m swanlab_mcp --transport sse

# 使用 HTTP 传输
python -m swanlab_mcp --transport http

# 查看版本
python -m swanlab_mcp --version
```

### 使用

配置完成后，重启 Claude Desktop，即可通过 MCP 协议与 SwanLab 进行交互。

可用工具：
- `swanlab_list_workspaces` - 列出工作空间
- `swanlab_create_project` - 创建项目
- `swanlab_list_projects` - 列出项目
- `swanlab_create_experiment` - 创建实验
- `swanlab_list_experiments` - 列出实验
- `swanlab_get_experiment` - 获取实验详情
- `swanlab_delete_experiment` - 删除实验

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