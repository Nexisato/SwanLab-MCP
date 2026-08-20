"""SwanLab MCP Pydantic models.

基于 swanlab >= 0.9.0 OpenAPI 原始响应结构设计（camelCase 字段通过别名映射），
对可能为空的字段放宽类型限制。
"""

from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from .utils import _normalize_to_dict, _normalize_to_list, _normalize_to_str


class User(BaseModel):
    """User (用户) model.

    当前认证用户的个人信息。
    """

    model_config = ConfigDict(extra="allow")

    name: str = Field(default="", description="用户显示名")
    username: str = Field(default="", description="用户名，即唯一ID")
    bio: str = Field(default="", description="个人简介")
    institution: str = Field(default="", description="所属机构")
    school: str = Field(default="", description="所属学校")
    email: str = Field(default="", description="邮箱")
    location: str = Field(default="", description="所在地")
    url: str = Field(default="", description="个人主页 URL")

    @field_validator("name", "username", "bio", "institution", "school", "email", "location", "url", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)


class Workspace(BaseModel):
    """Workspace (空间) model.

    空间是项目的集合，对应一个研发团队，分为个人空间(PERSON)和组织空间(TEAM)。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    username: str = Field(default="", description="空间用户名，即唯一ID")
    name: str = Field(default="", description="空间名称")
    role: str = Field(default="", description="当前登录用户在该空间中的角色：OWNER 或 MEMBER")
    workspace_type: str = Field(
        default="",
        description="空间类型：PERSON 或 TEAM",
        validation_alias=AliasChoices("type", "workspace_type"),
    )
    comment: str = Field(default="", description="空间备注")
    profile: Dict[str, Any] = Field(default_factory=dict, description="空间的介绍信息，包含简介、url、机构、邮箱")

    @field_validator("username", "name", "role", "workspace_type", "comment", mode="before")
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

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    project_id: str = Field(
        default="",
        description="项目ID",
        validation_alias=AliasChoices("cuid", "project_id"),
    )
    name: str = Field(default="", description="项目名")
    path: str = Field(default="", description="项目路径，格式为 username/project_name")
    description: str = Field(default="", description="项目描述")
    labels: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="项目标签列表，每项包含 name 和 colors",
        validation_alias=AliasChoices("projectLabels", "labels"),
    )
    visibility: str = Field(default="", description="项目可见性：PUBLIC 或 PRIVATE")
    created_at: Optional[str] = Field(
        default=None,
        description="项目创建时间",
        validation_alias=AliasChoices("createdAt", "created_at"),
    )
    updated_at: Optional[str] = Field(
        default=None,
        description="项目更新时间",
        validation_alias=AliasChoices("updatedAt", "updated_at"),
    )
    url: str = Field(default="", description="项目URL")
    count: Dict[str, Any] = Field(
        default_factory=dict,
        description="项目统计信息，包含 experiments（实验数）、collaborators（协作者数）等",
        validation_alias=AliasChoices("_count", "count"),
    )

    @field_validator("project_id", "name", "path", "description", "visibility", "url", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)

    @field_validator("labels", mode="before")
    @classmethod
    def _normalize_labels(cls, value: Any) -> List[Dict[str, Any]]:
        return [label for label in _normalize_to_list(value) if isinstance(label, dict)]

    @field_validator("count", mode="before")
    @classmethod
    def _normalize_count(cls, value: Any) -> Dict[str, Any]:
        return _normalize_to_dict(value)


class ProjectList(BaseModel):
    """Paginated project list.

    分页的项目列表。
    """

    model_config = ConfigDict(extra="allow")

    workspace: str = Field(default="", description="查询的工作空间用户名")
    page: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页条数")
    total: int = Field(default=0, description="项目总数")
    pages: int = Field(default=0, description="总页数")
    projects: List[Project] = Field(default_factory=list, description="当前页的项目列表")


class RunUser(BaseModel):
    """Run user information.

    实验用户信息。
    """

    model_config = ConfigDict(extra="allow")

    name: Optional[str] = Field(default=None, description="用户显示名")
    username: Optional[str] = Field(default=None, description="用户名")

    @field_validator("name", "username", mode="before")
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> Optional[str]:
        return _normalize_to_str(value) if value is not None else None


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
        return [str(req) for req in _normalize_to_list(value)]


class Run(BaseModel):
    """Run (实验) model.

    单次训练/推理任务，包含指标、配置、日志等数据。
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    run_id: str = Field(
        default="",
        description="实验ID，唯一标识符",
        validation_alias=AliasChoices("run_id", "id", "cuid"),
    )
    project_id: str = Field(default="", description="所属项目ID")
    name: str = Field(default="", description="实验名")
    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    description: str = Field(default="", description="实验描述")
    type: str = Field(default="", description="实验类型：CHAPTER 或 SUMMARY")
    state: str = Field(default="", description="实验状态：FINISHED、RUNNING、CRASHED、ABORTED、OFFLINE")
    group: str = Field(
        default="",
        description="实验分组",
        validation_alias=AliasChoices("cluster", "group"),
    )
    labels: List[Dict[str, Any]] = Field(default_factory=list, description="实验标签列表，每项包含 name 和 colors")
    created_at: Optional[str] = Field(
        default=None,
        description="实验创建时间",
        validation_alias=AliasChoices("createdAt", "created_at"),
    )
    finished_at: Optional[str] = Field(
        default=None,
        description="实验结束时间；未结束则为 None",
        validation_alias=AliasChoices("finishedAt", "finished_at"),
    )
    url: str = Field(default="", description="实验URL")
    job_type: str = Field(
        default="",
        description="任务类型",
        validation_alias=AliasChoices("job", "job_type"),
    )
    show: bool = Field(default=True, description="实验在图表对比视图的显示状态")
    root_pro_id: str = Field(
        default="",
        description="根实验所属项目ID（克隆实验场景），非克隆则为空",
        validation_alias=AliasChoices("rootProId", "root_pro_id"),
    )
    root_exp_id: str = Field(
        default="",
        description="根实验ID（克隆实验场景），非克隆则为空",
        validation_alias=AliasChoices("rootExpId", "root_exp_id"),
    )
    user: Optional[RunUser] = Field(default=None, description="实验用户信息")
    profile: Optional[RunProfile] = Field(default=None, description="实验配置信息")

    @field_validator(
        "run_id",
        "project_id",
        "name",
        "path",
        "description",
        "type",
        "state",
        "group",
        "url",
        "job_type",
        "root_pro_id",
        "root_exp_id",
        mode="before",
    )
    @classmethod
    def _normalize_str_fields(cls, value: Any) -> str:
        return _normalize_to_str(value)

    @field_validator("labels", mode="before")
    @classmethod
    def _normalize_labels(cls, value: Any) -> List[Dict[str, Any]]:
        return [label for label in _normalize_to_list(value) if isinstance(label, dict)]

    @field_validator("user", "profile", mode="before")
    @classmethod
    def _normalize_model_fields(cls, value: Any) -> Optional[Dict[str, Any]]:
        if value is None or value == "":
            return None
        if isinstance(value, dict):
            return value
        return None


class RunList(BaseModel):
    """Paginated run list.

    分页的实验列表。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="查询的项目路径，格式为 username/project_name")
    page: int = Field(default=1, description="当前页码")
    size: int = Field(default=20, description="每页条数")
    total: int = Field(default=0, description="实验总数")
    pages: int = Field(default=0, description="总页数")
    runs: List[Run] = Field(default_factory=list, description="当前页的实验列表")


class SeriesList(BaseModel):
    """Metric key list of a run.

    实验的指标键列表（对应 `swanlab api run series`）。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    metric_type: str = Field(default="SCALAR", description="指标类型：SCALAR 或 MEDIA")
    metric_class: str = Field(default="CUSTOM", description="指标分类：CUSTOM（用户自定义）或 SYSTEM（系统监控）")
    search: str = Field(default="", description="搜索关键词")
    keys: List[str] = Field(default_factory=list, description="指标键名列表")
    total: int = Field(default=0, description="指标键总数")


class MetricData(BaseModel):
    """Scalar metric query result.

    标量指标查询结果（对应 `swanlab api run metrics`）。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    keys: List[str] = Field(default_factory=list, description="请求的指标 key 列表")
    metric_type: str = Field(default="SCALAR", description="指标类型，固定为 SCALAR")
    sample: Optional[int] = Field(default=None, description="采样数量上限（最大 1500），全量导出时为 None")
    fetch_all: bool = Field(default=False, description="是否跳过采样获取全量数据")
    series: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="每个 key 一项，包含 metrics 数据点列表（step/value 等）以及 min/max/avg/median/latest 统计值",
    )
    total: int = Field(default=0, description="返回的指标序列个数")


class SummaryData(BaseModel):
    """Scalar metric summary result.

    标量指标统计摘要（对应 `swanlab api run summary`）。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    keys: Optional[List[str]] = Field(default=None, description="请求的指标 key 列表；为 None 表示全部标量指标")
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="以指标名为 key，值为统计摘要 {step, value, min, max, avg, median, stdDev, minMax}",
    )
    total: int = Field(default=0, description="返回的指标个数")


class MediaData(BaseModel):
    """Media metric query result.

    媒体指标查询结果（对应 `swanlab api run medias`）。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    keys: List[str] = Field(default_factory=list, description="请求的媒体指标 key 列表")
    step: Optional[int] = Field(default=0, description="获取的步数；为 None 或使用 fetch_all 时返回全部步数")
    fetch_all: bool = Field(default=False, description="是否获取全部步数的媒体数据")
    medias: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="每个 key 一项，包含 steps 列表和 metrics 数据（含可下载的 URL）",
    )
    total: int = Field(default=0, description="返回的媒体序列个数")


class LogData(BaseModel):
    """Console log query result.

    实验控制台日志查询结果（对应 `swanlab api run logs`）。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    offset: int = Field(default=0, description="日志分片偏移量")
    level: str = Field(default="INFO", description="日志级别：DEBUG、INFO、WARN、ERROR")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="日志条目列表，每项包含 level、message 等")
    count: int = Field(default=0, description="返回的日志条数")


class LogExport(BaseModel):
    """Console log export result.

    实验控制台日志导出结果（对应 `swanlab api run export-logs`），返回带签名的下载 URL。
    """

    model_config = ConfigDict(extra="allow")

    path: str = Field(default="", description="实验路径，格式为 username/project_name/run_id")
    start: int = Field(default=0, description="导出起始行（0-based）")
    rows: int = Field(default=0, description="导出行数")
    url: str = Field(default="", description="日志文件下载 URL（预签名，有时效性）")
