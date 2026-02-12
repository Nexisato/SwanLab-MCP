"""Workspace related MCP tools."""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import Project, Workspace
from ._normalize import ensure_username, to_plain_dict, to_plain_dict_list


class WorkspaceTools:
    """SwanLab Workspace management tools."""

    def __init__(self, api: Api):
        self.api = api

    async def list_workspaces(self, username: Optional[str] = None) -> List[Workspace]:
        """
        List all workspaces accessible to the current user.

        Returns:
            List of Workspace objects containing:
            - username: 空间用户名，即唯一ID
            - name: 空间名称
            - role: 当前登录用户在该空间中的角色 (OWNER/MEMBER)
            - workspace_type: 空间类型 (PERSON/TEAM)
            - profile: 空间的介绍信息
        """
        try:
            normalized_username = ensure_username(username)
            workspaces = (
                self.api.workspaces(username=normalized_username) if normalized_username else self.api.workspaces()
            )
            return [Workspace(**to_plain_dict(ws)) for ws in workspaces]
        except Exception as e:
            raise RuntimeError(f"Failed to list workspaces: {str(e)}") from e

    async def get_workspace(self, username: Optional[str] = None) -> Workspace:
        """
        Get a specific workspace by username.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            Workspace object with detailed information
        """
        try:
            normalized_username = ensure_username(username)
            ws = self.api.workspace(username=normalized_username) if normalized_username else self.api.workspace()
            return Workspace(**to_plain_dict(ws))
        except Exception as e:
            workspace_name = username if username else "<current-user>"
            raise RuntimeError(f"Failed to get workspace '{workspace_name}': {str(e)}") from e

    async def list_projects_in_workspace(self, username: Optional[str] = None) -> List[Project]:
        """
        List all projects in a specific workspace.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            List of Project objects
        """
        try:
            normalized_username = ensure_username(username)
            ws = self.api.workspace(username=normalized_username) if normalized_username else self.api.workspace()
            projects = ws.projects()
            return [Project(**proj_data) for proj_data in to_plain_dict_list(projects)]
        except Exception as e:
            workspace_name = username if username else "<current-user>"
            raise RuntimeError(f"Failed to list projects in workspace '{workspace_name}': {str(e)}") from e


def register_workspace_tools(mcp: FastMCP, api: Api) -> None:
    """
    Register workspace-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab Api instance
    """
    workspace_tools = WorkspaceTools(api)

    @mcp.tool(
        name="swanlab_list_workspaces",
        description="List all workspaces accessible to the current user.",
        annotations=ToolAnnotations(
            title="List all workspaces accessible to the current user.",
            readOnlyHint=True,
        ),
    )
    async def list_workspaces(username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all workspaces accessible to the current user.

        Args:
            username: 可选，空间用户名。为空时返回当前用户可访问的全部空间。

        Returns:
            List of workspaces with their names, usernames, roles, and types.
        """
        workspaces = await workspace_tools.list_workspaces(username=username)
        return [ws.model_dump() for ws in workspaces]

    @mcp.tool(
        name="swanlab_get_workspace",
        description="Get detailed information about a specific workspace.",
        annotations=ToolAnnotations(
            title="Get detailed information about a specific workspace.",
            readOnlyHint=True,
        ),
    )
    async def get_workspace(username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific workspace.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            Workspace details including name, role, type, and profile.
        """
        workspace = await workspace_tools.get_workspace(username)
        return workspace.model_dump()

    @mcp.tool(
        name="swanlab_list_projects_in_workspace",
        description="List all projects in a specific workspace by username.",
        annotations=ToolAnnotations(
            title="List all projects in a specific workspace.",
            readOnlyHint=True,
        ),
    )
    async def list_projects_in_workspace(username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all projects in a specific workspace.

        Args:
            username: 空间用户名，即唯一ID；不传时默认当前登录用户

        Returns:
            List of projects with their details.
        """
        projects = await workspace_tools.list_projects_in_workspace(username)
        return [project.model_dump() for project in projects]
