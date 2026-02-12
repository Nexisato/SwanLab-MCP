"""Project related MCP tools."""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import Project, Run
from ._normalize import ensure_project_path, ensure_project_sort, ensure_username, to_plain_dict, to_plain_dict_list


class ProjectTools:
    """SwanLab Project management tools."""

    def __init__(self, api: Api):
        self.api = api

    async def list_projects(
        self,
        path: Optional[str] = None,
        sort: Optional[str] = None,
        search: Optional[str] = None,
        detail: bool = True,
    ) -> List[Project]:
        """
        List all projects with optional filtering.

        Args:
            path: 空间路径（用户名），格式为 username，用于筛选指定空间下的所有项目
            sort: 排序方式，可选：created_at（创建时间）、updated_at（更新时间）
            search: 搜索关键词，模糊匹配项目名
            detail: 是否返回项目详细信息（如描述、标签），默认为 True

        Returns:
            List of Project objects containing:
            - name: 项目名
            - path: 项目路径，格式为 username/project_name
            - description: 项目描述
            - labels: 项目标签
            - visibility: PUBLIC 或 PRIVATE
            - created_at/updated_at: 时间戳
            - url: 项目URL
            - count: 统计信息
        """
        try:
            kwargs = {"detail": detail}
            if path:
                kwargs["path"] = ensure_username(path)
            if sort:
                kwargs["sort"] = ensure_project_sort(sort)
            if search:
                kwargs["search"] = search

            projects = self.api.projects(**kwargs)
            return [Project(**proj_data) for proj_data in to_plain_dict_list(projects)]
        except Exception as e:
            raise RuntimeError(f"Failed to list projects: {str(e)}") from e

    async def get_project(self, path: str) -> Project:
        """
        Get detailed information about a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            Project object with detailed information
        """
        try:
            normalized_path = ensure_project_path(path)
            proj = self.api.project(path=normalized_path)
            return Project(**to_plain_dict(proj))
        except Exception as e:
            raise RuntimeError(f"Failed to get project '{path}': {str(e)}") from e

    async def list_runs_in_project(self, path: str) -> List[Run]:
        """
        List all runs (experiments) in a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            List of Run objects
        """
        try:
            normalized_path = ensure_project_path(path)
            proj = self.api.project(path=normalized_path)
            runs = proj.runs()
            return [Run(**run_data) for run_data in to_plain_dict_list(runs)]
        except Exception as e:
            raise RuntimeError(f"Failed to list runs in project '{path}': {str(e)}") from e


def register_project_tools(mcp: FastMCP, api: Api) -> None:
    """
    Register project-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab Api instance
    """
    project_tools = ProjectTools(api)

    @mcp.tool(
        name="swanlab_list_projects",
        description="List all projects with optional filtering by workspace, sort, and search.",
        annotations=ToolAnnotations(
            title="List all projects with filtering options.",
            readOnlyHint=True,
        ),
    )
    async def list_projects(
        path: Optional[str] = None,
        sort: Optional[str] = None,
        search: Optional[str] = None,
        detail: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        List all projects with optional filtering.

        Args:
            path: 空间用户名，用于筛选指定空间下的所有项目
            sort: 排序方式，可选：created_at（创建时间）、updated_at（更新时间）
            search: 搜索关键词，模糊匹配项目名
            detail: 是否返回项目详细信息，默认为 True

        Returns:
            List of projects with details including name, path, description, visibility, etc.
        """
        projects = await project_tools.list_projects(path=path, sort=sort, search=search, detail=detail)
        return [proj.model_dump() for proj in projects]

    @mcp.tool(
        name="swanlab_get_project",
        description="Get detailed information about a specific project.",
        annotations=ToolAnnotations(
            title="Get detailed information about a specific project.",
            readOnlyHint=True,
        ),
    )
    async def get_project(path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            Project details including metadata and statistics.
        """
        project_obj = await project_tools.get_project(path)
        return project_obj.model_dump()

    @mcp.tool(
        name="swanlab_list_runs_in_project",
        description="List all runs (experiments) in a specific project.",
        annotations=ToolAnnotations(
            title="List all runs in a project.",
            readOnlyHint=True,
        ),
    )
    async def list_runs_in_project(path: str) -> List[Dict[str, Any]]:
        """
        List all runs (experiments) in a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            List of runs with their details.
        """
        runs = await project_tools.list_runs_in_project(path)
        return [run.model_dump() for run in runs]
