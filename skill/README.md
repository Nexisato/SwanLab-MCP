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
以 `Claude Code` 为例 (其他 Coding Agent 配置方式同理)

```bash
# 配置 skill（复制到 Claude Code 配置目录）
cp -r swanlab-api-skill ~/.claude/skills/

# 重启 Claude Code 使配置生效
```

配置完成后，在 Claude Code 中使用 `/swanlab-api-skill` 命令调用。



## SKILL Doc

See [swanlab-api-skill/SKILL.md](./swanlab-api-skill/SKILL.md)
