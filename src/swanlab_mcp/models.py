from typing import Dict

from pydantic import BaseModel


class Experiment(BaseModel):
    cuid: str  # 实验CUID, 唯一标识符
    name: str  # 实验名
    description: str = ""  # 实验描述
    state: str  # 实验状态, 'FINISHED' 或 'RUNNING'
    show: bool  # 显示状态
    createdAt: str  # e.g., '2024-11-23T12:28:04.286Z'
    finishedAt: str = ""  # e.g., '2024-11-23T12:28:04.286Z'
    user: Dict[str, str]  # 实验创建者, 包含 'username' 与 'name'
    profile: Dict  # 实验相关配置


class Project(BaseModel):
    cuid: str  # 项目CUID, 唯一标识符
    name: str  # 项目名
    description: str = ""  # 项目描述
    visibility: str  # 可见性, 'PUBLIC' 或 'PRIVATE'
    createdAt: str  # e.g., '2024-11-23T12:28:04.286Z'
    updatedAt: str  # e.g., '2024-11-23T12:28:04.286Z'
    group: Dict[str, str]  # 工作空间信息, 包含 'type', 'username', 'name'
    count: Dict[str, int] = {}  # 项目的统计信息
