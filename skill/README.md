# SwanLab API Skill

通过 SwanLab OpenAPI 获取实验(runs)、项目(projects)、工作空间(workspace)等资源的数据，支持 metrics 导出为 JSON 文件。

## 环境要求

- Python >= 3.8
- swanlab >= 0.7.8
- pandas

## 环境变量

```bash
# 设置 API 密钥
export SWANLAB_API_KEY="your-api-key"

# 可选：指定 SwanLab 主机（默认 https://swanlab.cn）
export SWANLAB_HOST="https://swanlab.cn"
```

获取 API 密钥：https://swanlab.cn/space/~/settings

## 快速开始

```bash
# 列出 workspaces
python -m scripts.swanlab_cli workspaces list

# 列出 projects
python -m scripts.swanlab_cli projects list

# 获取 run 信息
python -m scripts.swanlab_cli runs get username/project/exp_id

# 获取 run config
python -m scripts.swanlab_cli runs config username/project/exp_id

# 获取 run metadata（环境信息）
python -m scripts.swanlab_cli runs metadata username/project/exp_id

# 获取 run metrics（保存为 JSON 文件）
python -m scripts.swanlab_cli runs metrics username/project/exp_id "loss,accuracy" -o metrics
```

## 命令概览

| 命令 | 说明 |
|------|------|
| `workspaces list` | 列出所有 workspaces |
| `workspaces get [username]` | 获取 workspace 信息 |
| `projects list [username]` | 列出 projects |
| `projects get PATH` | 获取 project 信息 |
| `runs list PROJECT_PATH` | 列出实验 runs |
| `runs get RUN_PATH` | 获取 run 信息 |
| `runs config RUN_PATH` | 获取 run 配置 |
| `runs metadata RUN_PATH` | 获取 run 环境元信息 |
| `runs requirements RUN_PATH` | 获取 run Python 依赖 |
| `runs metrics RUN_PATH KEYS` | 获取 metrics（保存 JSON） |

## 输出规则

- 只有 `runs metrics` 命令会保存 JSON 文件（默认保存到 `.cache/` 目录）
- 其他命令只输出到控制台

## Path 格式

- Project: `username/project_name` 或简写为 `project_name`
- Run: `username/project_name/exp_id` 或简写为 `project_name/exp_id`

## 详细文档

See [swanlab-api-skill/SKILL.md](./swanlab-api-skill/SKILL.md)
