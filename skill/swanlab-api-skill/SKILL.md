---
name: swanlab-api-skill
description: 通过 SwanLab OpenAPI 获取实验(experiments/runs)、项目(projects)、工作空间 (workspace)等资源的数据，支持 metrics 导出为 JSON 文件
---
# triggers:
  - 当用户需要获取 SwanLab 实验数据时
  - 当用户需要导出 metrics 到 JSON 时
  - 当用户需要获取 workspace、project、run 信息时
  - 当用户需要获取实验的 metadata、config、requirements 时

## 环境要求

- Python >= 3.8
- swanlab >= 0.7.8
- pandas (用于 metrics 数据处理)

## 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `SWANLAB_API_KEY` | 条件必需* | SwanLab API 密钥 |
| `SWANLAB_HOST` | 否 | SwanLab 主机地址，默认 `https://swanlab.cn` |

获取 API 密钥：https://swanlab.cn/space/~/settings

### API Key 获取优先级 【最先执行】

1. **环境变量** `SWANLAB_API_KEY`（优先）
2. **Netrc 文件** `~/.swanlab/netrc` 中的 `password` 字段

**Netrc 文件配置示例：**

```bash
# 创建 netrc 文件
mkdir -p ~/.swanlab
cat > ~/.swanlab/netrc << 'EOF'
machine https://api.swanlab.cn
        login https://swanlab.cn
        password your_api_key_here
EOF
chmod 600 ~/.swanlab/netrc
```

> 注：环境变量优先级高于 netrc 文件。如果设置了 `SWANLAB_API_KEY`，将忽略 netrc 中的配置。

## 核心规则

1. **Username 默认规则**:
   - 未指定 `username` 时，自动调用 `api.workspaces()` 获取 `PERSON` 类型的 workspace 作为默认
   - Path 支持简写：`project_name/exp_id` 会自动补全为 `username/project_name/exp_id`

2. **输出规则**:
   - 只有 `runs metrics` 命令会保存 JSON 文件
   - 其他所有命令都只输出到控制台（stdout）

3. **Metrics 输出**:
   - 使用 `-o` 指定文件名，默认保存到 `./.cache/` 目录（自动创建）
   - 超过 8192 条记录时自动分片保存，命名格式 `[name]-[chunk_idx:04d].json`
   - 不分片时文件名为 `[name].json`

4. **实验分析前置规则**（重要）：
   - 在获取实验指标 Metrics 之前，**必须先获取实验元信息**（runs get、runs config）
   - 元信息包括：实验名称、状态、超参数配置等
   - 禁止直接获取 metrics 而不了解实验的基本信息和配置

## 意图识别

当用户需要进行实验分析、实验对比或实验总结时，按以下步骤获取实验元信息：

1. **获取实验基础信息**（必需）：
   ```bash
   python -m scripts.swanlab_cli runs get RUN_PATH
   ```
   - 了解实验名称、状态、创建时间、运行时长
   - 获取实验标签和分组信息

2. **获取实验配置 Config**（必需）：
   ```bash
   python -m scripts.swanlab_cli runs config RUN_PATH
   ```
   - 获取超参数配置（学习率、批次大小、模型架构等）
   - 理解实验的目的和设置

3. **获取实验环境 Metadata**（建议）：
   ```bash
   python -m scripts.swanlab_cli runs metadata RUN_PATH
   ```
   - 获取 Python 版本、操作系统、硬件信息（GPU/CPU）
   - 获取 Git 提交信息（代码版本）
   - 用于复现实验环境和排查环境问题

4. **获取 Python 依赖 Requirements**（可选）：
   ```bash
   python -m scripts.swanlab_cli runs requirements RUN_PATH
   ```
   - 了解实验使用的库版本
   - 用于环境复现

5. **列出可用指标键名 Metric Keys**（按需，在获取 Metrics 前使用）：
   ```bash
   python -m scripts.swanlab_cli runs metric-keys RUN_PATH
   ```
   - 列出实验的所有可用 metric keys 及其类型
   - 在不知道指标名称时使用，获取后再调用 metrics 命令

6. **获取实验指标 Metrics**（按需，必须在获取元信息之后）：
   ```bash
   python -m scripts.swanlab_cli runs metrics RUN_PATH "key1,key2" -o metrics
   ```
   - 获取具体的训练/评估指标数据
   - 用于绘制图表、趋势分析
   - ⚠️ **必须在获取 runs get 和 runs config 之后再执行**

**分析流程建议**：
- 单实验分析：先获取基础信息 + Config → 分析实验目的和配置 → 用 metric-keys 发现指标 → 按需获取 Metrics 进行指标分析
- 多实验对比：获取各实验 Config 找出变量差异 → 对比 Metrics 分析不同配置的效果
- 实验复现：获取 Config + Metadata + Requirements → 完整还原实验环境

## 命令行工具

统一 CLI 工具：`python -m scripts.swanlab_cli`

### Workspaces 命令

```bash
# 列出所有 workspaces（输出到控制台）
python -m scripts.swanlab_cli workspaces list

# 获取指定 workspace 信息（默认 personal）
python -m scripts.swanlab_cli workspaces get [USERNAME]

# 获取 workspace 下的所有 projects
python -m scripts.swanlab_cli workspaces projects [USERNAME]
```

### Projects 命令

```bash
# 列出 projects（默认使用 personal workspace）
python -m scripts.swanlab_cli projects list [USERNAME] 
  [--sort {created_at,updated_at}]
  [--search SEARCH]
  [--detail true/false]

# 获取 project 信息（使用默认 username）
python -m scripts.swanlab_cli projects get PATH

# 获取 project 下的 runs
python -m scripts.swanlab_cli projects runs PATH 
  [--filter KEY=VALUE]
```

### Runs/Experiments 命令

```bash
# 列出 runs（输出到控制台）
python -m scripts.swanlab_cli runs list PROJECT_PATH 
  [--filter KEY=VALUE]

# 获取 run 信息
python -m scripts.swanlab_cli runs get RUN_PATH

# 获取 run 的 config
python -m scripts.swanlab_cli runs config RUN_PATH

# 获取 run 的 metadata（环境信息、Python版本、硬件信息等）
python -m scripts.swanlab_cli runs metadata RUN_PATH

# 获取 run 的 requirements（Python 依赖）
python -m scripts.swanlab_cli runs requirements RUN_PATH

# 列出 run 的所有可用 metric keys
python -m scripts.swanlab_cli runs metric-keys RUN_PATH

# 获取 run 的 metrics（唯一保存 JSON 文件的命令）
python -m scripts.swanlab_cli runs metrics RUN_PATH KEYS
  [--x-axis X_AXIS]
  [--sample SAMPLE]
  [--chunk-size CHUNK_SIZE]
  [-o OUTPUT]
```

## 使用示例

### Workspaces 操作

```bash
export SWANLAB_API_KEY="your-api-key"

# 获取所有 workspaces（控制台输出）
python -m scripts.swanlab_cli workspaces list

# 获取默认 workspace 信息
python scripts/swanlab_cli.py workspaces get

# 获取指定 workspace 信息
python scripts/swanlab_cli.py workspaces get myusername
```

### Projects 操作

```bash
# 列出默认用户的所有 projects
python scripts/swanlab_cli.py projects list

# 列出指定用户的 projects，按更新时间排序
python scripts/swanlab_cli.py projects list otheruser --sort updated_at

# 搜索 projects
python scripts/swanlab_cli.py projects list --search "image-classification"

# 获取 project 信息（使用默认 username）
python scripts/swanlab_cli.py projects get myproject

# 获取 project 信息（完整 path）
python scripts/swanlab_cli.py projects get username/myproject
```

### Runs 操作

```bash
# 列出 project 下的所有 runs
python scripts/swanlab_cli.py runs list myproject

# 筛选 runs（如只获取已完成的）
python scripts/swanlab_cli.py runs list myproject --filter state=FINISHED

# 筛选 runs（多条件）
python scripts/swanlab_cli.py runs list myproject \
  --filter state=FINISHED \
  --filter "config.batch_size=64"

# 获取 run 信息
python scripts/swanlab_cli.py runs get myproject/exp_abc123

# 获取 run 信息（完整 path）
python scripts/swanlab_cli.py runs get username/myproject/exp_abc123
```

### 获取实验元数据

```bash
# 获取 config（输出到控制台）
python scripts/swanlab_cli.py runs config myproject/exp_abc123

# 获取 metadata（Python版本、硬件信息、Git信息等）
python scripts/swanlab_cli.py runs metadata myproject/exp_abc123

# 获取 requirements（Python依赖）
python scripts/swanlab_cli.py runs requirements myproject/exp_abc123

# 重定向保存（如果需要）
python scripts/swanlab_cli.py runs config myproject/exp_abc123 > ./config.json
```

### 列出可用 Metric Keys

```bash
# 列出 run 的所有可用 metric keys
python scripts/swanlab_cli.py runs metric-keys myproject/exp_abc123

# 使用完整 path
python scripts/swanlab_cli.py runs metric-keys username/myproject/exp_abc123
```

### 获取 Metrics（唯一保存文件的命令）

```bash
# 获取单个指标（输出到控制台）
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss"

# 获取多个指标（逗号分隔）
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss,accuracy,learning_rate"

# 指定 x 轴
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss" --x-axis accuracy

# 采样限制
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss" --sample 1000

# 保存到 .cache/ 目录（自动创建目录）
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss,accuracy" -o metrics
# 输出: .cache/metrics.json（≤8192条）
# 或: .cache/metrics-0001.json, .cache/metrics-0002.json...（>8192条）

# 保存到指定路径
python scripts/swanlab_cli.py runs metrics myproject/exp_abc123 "loss,accuracy" \
  --chunk-size 8192 \
  -o ./data/metrics
# 输出: ./data/metrics.json 或 ./data/metrics-0001.json...
```

## Path 格式说明

| 资源类型 | 完整格式 | 简写格式 |
|----------|----------|----------|
| Workspace | - | username |
| Project | username/project_name | project_name（自动补全 username） |
| Run | username/project_name/exp_id | project_name/exp_id（自动补全 username） |

## 输出数据结构

### Workspace

```json
{
  "username": "myuser",
  "name": "My Name",
  "workspace_type": "PERSON",
  "role": "OWNER",
  "profile": {
    "bio": "...",
    "url": "...",
    "company": "...",
    "email": "..."
  }
}
```

### Project

```json
{
  "name": "image-classification",
  "path": "myuser/image-classification",
  "description": "图像分类实验",
  "labels": ["cv", "resnet"],
  "created_at": "2025-01-01T00:00:00.000Z",
  "updated_at": "2025-01-10T00:00:00.000Z",
  "url": "https://swanlab.cn/@myuser/image-classification",
  "visibility": "PUBLIC",
  "count": {
    "experiments": 10,
    "collaborators": 2
  }
}
```

### Run

```json
{
  "name": "exp-001",
  "path": "myuser/myproject/exp_abc123",
  "id": "exp_abc123",
  "state": "FINISHED",
  "group": ["A", "B"],
  "labels": ["test", "v1"],
  "created_at": "2025-01-01T00:00:00.000Z",
  "finished_at": "2025-01-02T00:00:00.000Z",
  "url": "https://swanlab.cn/...",
  "job_type": "training",
  "show": true,
  "user": {
    "is_self": true,
    "username": "myuser"
  }
}
```

### Metric Keys

```json
{
  "path": "myuser/myproject/exp_abc123",
  "keys": [
    {"key": "loss", "type": "SCALAR", "class": "STABLE", "error": null},
    {"key": "accuracy", "type": "SCALAR", "class": "STABLE", "error": null}
  ],
  "total": 2
}
```

### Metrics

```json
[
  {"step": 1, "timestamp": 1704067200, "loss": 0.5, "accuracy": 0.7},
  {"step": 2, "timestamp": 1704067260, "loss": 0.4, "accuracy": 0.8}
]
```

### Metadata

```json
{
  "python_version": "3.10.0",
  "os": "Linux-5.15.0",
  "hostname": "server-01",
  "git": {
    "remote": "https://github.com/...",
    "commit_id": "abc123..."
  },
  "gpu": ["NVIDIA A100"],
  "cpu": "Intel Xeon",
  "memory": "256GB"
}
```

## 错误处理

脚本会在以下情况报错退出：

1. `SWANLAB_API_KEY` 未设置
2. Path 格式不正确
3. 资源不存在
4. API 请求失败

错误信息会输出到 stderr。

## 参考文档

- SwanLab OpenAPI 文档： `resources/swanlab_api_docs.md`
- SwanLab 官网：https://swanlab.cn
