"""Project related MCP tools.

项目管理工具，用于获取项目信息和项目下的实验列表。
"""

from typing import Any, Dict, Optional

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ..client import SwanLabClient
from ..constants import VALID_PAGE_SIZES
from ..models import Project, ProjectList
from ..utils import validate_page, validate_project_path, validate_workspace_name


class ProjectTools:
    """SwanLab Project management tools.

    项目是实验的集合，对应一个研发任务（如"图像分类"）。
    对应 OpenAPI 端点 GET /project/{username}（分页列表）与 GET /project/{path}（详情）。
    """

    def __init__(self, client: SwanLabClient):
        self.client = client

    async def list_projects(
        self,
        workspace: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> ProjectList:
        """
        List projects under a workspace, paginated.

        Args:
            workspace: 工作空间用户名，用于筛选指定空间下的所有项目
            page: 页码，>= 1
            page_size: 每页条数，必须是 10/12/15/20/24/27/50/100 之一
            search: 搜索关键词，模糊匹配项目名
            sort: 排序字段，如 created_at（创建时间）、updated_at（更新时间）

        Returns:
            ProjectList object with pagination info and project list
        """
        try:
            normalized_workspace = validate_workspace_name(workspace)
            validate_page(page, page_size, VALID_PAGE_SIZES)
            params: Dict[str, Any] = {"page": page, "size": page_size, "detail": True}
            if search and search.strip():
                params["search"] = search.strip()
            if sort and sort.strip():
                params["sort"] = sort.strip()
            data = self.client.get_json(f"/project/{normalized_workspace}", params=params)
            if not isinstance(data, dict):
                raise RuntimeError(f"unexpected response type {type(data).__name__}.")
            projects = [Project(**item) for item in data.get("list", []) if isinstance(item, dict)]
            for project in projects:
                if not project.path:
                    project.path = f"{normalized_workspace}/{project.name}"
                if not project.url:
                    project.url = self.client.web_url(f"@{project.path}")
            return ProjectList(
                workspace=normalized_workspace,
                page=page,
                size=data.get("size", page_size),
                total=data.get("total", len(projects)),
                pages=data.get("pages", 0),
                projects=projects,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to list projects for workspace '{workspace}': {str(e)}") from e

    async def get_project(self, path: str) -> Project:
        """
        Get detailed information about a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            Project object with detailed information
        """
        try:
            normalized_path = validate_project_path(path)
            data = self.client.get_json(f"/project/{normalized_path}")
            if not isinstance(data, dict):
                raise RuntimeError(f"unexpected response type {type(data).__name__}.")
            project = Project(**data)
            if not project.path:
                project.path = normalized_path
            if not project.url:
                project.url = self.client.web_url(f"@{project.path}")
            return project
        except Exception as e:
            raise RuntimeError(f"Failed to get project '{path}': {str(e)}") from e


def register_project_tools(mcp: FastMCP, client: SwanLabClient) -> None:
    """
    Register project-related MCP tools.

    Args:
        mcp: FastMCP server instance
        client: SwanLab OpenAPI client
    """
    project_tools = ProjectTools(client)

    @mcp.tool(
        name="swanlab_list_projects",
        title="List projects under a workspace.",
        description="List projects under a workspace with pagination and optional search/sort. "
        "项目是实验的集合，对应一个研发任务。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def list_projects(
        workspace: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List projects under a workspace, paginated.

        Args:
            workspace: 工作空间用户名
            page: 页码，>= 1，默认 1
            page_size: 每页条数，必须是 10/12/15/20/24/27/50/100 之一，默认 20
            search: 可选，搜索关键词，模糊匹配项目名
            sort: 可选，排序字段，如 created_at、updated_at

        Returns:
            Paginated project list with name, path, description, visibility and statistics.
            返回分页的项目列表，包含名称、路径、描述、可见性和统计信息。
        """
        project_list = await project_tools.list_projects(
            workspace=workspace,
            page=page,
            page_size=page_size,
            search=search,
            sort=sort,
        )
        return project_list.model_dump()

    @mcp.tool(
        name="swanlab_get_project",
        title="Get detailed information about a specific project.",
        description="Get detailed information about a specific project. 获取指定项目的详细信息。",
        annotations=ToolAnnotations(readOnlyHint=True),
    )
    async def get_project(path: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.

        Args:
            path: 项目路径，格式为 username/project_name

        Returns:
            Project details including metadata and statistics.
            返回项目详情，包含元数据和统计信息。
        """
        project_obj = await project_tools.get_project(path)
        return project_obj.model_dump()
