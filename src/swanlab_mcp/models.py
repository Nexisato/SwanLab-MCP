"""SwanLab MCP Pydantic models.

基于 SwanLab OpenAPI 文档设计，对可能为空的字段放宽类型限制。
"""

from collections.abc import Mapping
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from .utils import _normalize_to_dict, _normalize_to_list, _normalize_to_str


class Workspace(BaseModel):
    """Workspace (空间) model.

    空间是项目的集合，对应一个研发团队，分为个人空间(PERSON)和组织空间(TEAM)。
    """

    model_config = ConfigDict(extra="allow")

    username: str = Field(default="", description="空间用户名，即唯一ID")
    name: str = Field(default="", description="空间名称")
    role: str = Field(default="", description="当前登录用户在该空间中的角色：OWNER 或 MEMBER")
    workspace_type: str = Field(default="", description="空间类型：PERSON 或 TEAM")
    profile: Dict[str, Any] = Field(default_factory=dict, description="空间的介绍信息，包含简介、url、机构、邮箱")

    @field_validator("username", "name", "role", "workspace_type", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)

    @field_validator("profile", mode="before")
    @classmethod
    def _normalize_profile(cls, value: Any) -> Dict[str, Any]:
        return _normalize_to_dict(value)


class Project(BaseModel):
    """Project (项目) model.

    项目是实验的集合，对应一个研发任务。
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(default="", description="项目名")
    path: str = Field(default="", description="项目路径，格式为 username/project_name")
    description: str = Field(default="", description="项目描述")
    labels: List[str] = Field(default_factory=list, description="项目标签，格式为 [label1, label2, ...]")
    visibility: str = Field(default="", description="项目可见性：PUBLIC 或 PRIVATE")
    created_at: Optional[str] = Field(default=None, description="项目创建时间，ISO 8601 UTC 格式")
    updated_at: Optional[str] = Field(default=None, description="项目更新时间，ISO 8601 UTC 格式")
    url: str = Field(default="", description="项目URL")
    count: Dict[str, Any] = Field(default_factory=dict, description="项目统计信息，包含实验个数、协作者数量等")

    @field_validator("name", "path", "description", "visibility", "url", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)

    @field_validator("labels", mode="before")
    @classmethod
    def _normalize_labels(cls, value: Any) -> List[str]:
        return _normalize_to_list(value)

    @field_validator("count", mode="before")
    @classmethod
    def _normalize_count(cls, value: Any) -> Dict[str, Any]:
        return _normalize_to_dict(value)


class RunUser(BaseModel):
    """Run user information.

    实验用户信息。
    """

    model_config = ConfigDict(extra="allow")

    is_self: Optional[bool] = Field(default=None, description="是否为当前登录用户")
    username: Optional[str] = Field(default=None, description="用户名")


class RunProfile(BaseModel):
    """Run profile data.

    实验配置信息，包含 conda、config、metadata、requirements 属性。
    """

    model_config = ConfigDict(extra="allow")

    conda: Dict[str, Any] = Field(default_factory=dict, description="Conda 环境信息")
    config: Dict[str, Any] = Field(default_factory=dict, description="实验配置")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="环境元数据，如 Python 版本、硬件信息")
    requirements: List[str] = Field(default_factory=list, description="Python 包依赖信息")

    @field_validator("conda", "config", "metadata", mode="before")
    @classmethod
    def _normalize_dict_fields(cls, value: Any) -> Dict[str, Any]:
        return _normalize_to_dict(value)

    @field_validator("requirements", mode="before")
    @classmethod
    def _normalize_requirements(cls, value: Any) -> List[str]:
        return _normalize_to_list(value)


class Run(BaseModel):
    """Run (实验) model.

    单次训练/推理任务，包含指标、配置、日志等数据。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str = Field(
        default="",
        description="实验ID，唯一标识符",
        validation_alias=AliasChoices("id", "experiment_id"),
    )
    name: str = Field(default="", description="实验名")
    path: str = Field(default="", description="实验路径，格式为 username/project_name/experiment_id")
    description: str = Field(default="", description="实验描述")
    state: str = Field(default="", description="实验状态：FINISHED、RUNNING、CRASHED、ABORTED")
    group: List[str] = Field(default_factory=list, description="实验组，格式为 ['A', 'B', 'C']")
    labels: List[str] = Field(default_factory=list, description="实验标签，格式为 [label1, label2, ...]")
    created_at: Optional[str] = Field(default=None, description="实验创建时间，ISO 8601 UTC 格式")
    finished_at: Optional[str] = Field(default=None, description="实验结束时间，ISO 8601 UTC 格式；未结束则为 None")
    url: str = Field(default="", description="实验URL")
    job_type: str = Field(default="", description="任务类型")
    show: bool = Field(default=True, description="实验在图表对比视图的显示状态")
    user: Optional[RunUser] = Field(default=None, description="实验用户信息")
    profile: Optional[RunProfile] = Field(default=None, description="实验配置信息")

    @field_validator("id", "name", "path", "description", "state", "url", "job_type", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)

    @field_validator("group", "labels", mode="before")
    @classmethod
    def _normalize_list_fields(cls, value: Any) -> List[str]:
        return _normalize_to_list(value)

    @field_validator("user", mode="before")
    @classmethod
    def _normalize_user(cls, value: Any) -> Optional[Dict[str, Any]]:
        if value is None or value == "":
            return None
        if isinstance(value, Mapping):
            return dict(value)
        return None

    @field_validator("profile", mode="before")
    @classmethod
    def _normalize_profile(cls, value: Any) -> Optional[Dict[str, Any]]:
        if value is None or value == "":
            return None
        if isinstance(value, Mapping):
            return dict(value)
        return None


class MetricTable(BaseModel):
    """Run metric query result.

    指标查询结果。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/experiment_id")
    keys: List[str] = Field(default_factory=list, description="请求的指标 key 列表")
    x_axis: str = Field(default="step", description="指标数据的 X 轴字段")
    sample: Optional[int] = Field(default=None, description="采样数量")
    columns: List[str] = Field(default_factory=list, description="返回数据的列名")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="指标数据行列表")
    total: int = Field(default=0, description="指标数据总行数")
