"""Workspace related MCP tools.

工作空间管理工具，用于获取用户可访问的空间信息。
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import Api

from ..models import Workspace
from ..utils import to_plain_dict, validate_workspace_path


class WorkspaceTools:
    """SwanLab Workspace management tools.

    工作空间是项目的集合，对应一个研发团队（如"SwanLab"），分为个人空间（PERSON）和组织空间（TEAM）。
    """

    def __init__(self, api: Api):
        self.api = api

    async def list_workspaces(self, username: Optional[str] = None) -> List[Workspace]:
        """
        List all workspaces accessible to the current user.

        Args:
            username: 可选，空间用户名。为空时返回当前用户可访问的全部空间。

        Returns:
            List of Workspace objects containing:
            - username: 空间用户名，即唯一ID
            - name: 空间名称
            - role: 当前登录用户在该空间中的角色 (OWNER/MEMBER)
            - workspace_type: 空间类型 (PERSON/TEAM)
            - profile: 空间的介绍信息
        """
        try:
            normalized_username = validate_workspace_path(username)
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
            normalized_username = validate_workspace_path(username)
            ws = self.api.workspace(username=normalized_username) if normalized_username else self.api.workspace()
            return Workspace(**to_plain_dict(ws))
        except Exception as e:
            workspace_name = username if username else "<current-user>"
            raise RuntimeError(f"Failed to get workspace '{workspace_name}': {str(e)}") from e


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
        description="List all workspaces accessible to the current user. 工作空间是项目的集合，对应一个研发团队。",
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
            返回空间列表，包含用户名、名称、角色和类型等信息。
        """
        workspaces = await workspace_tools.list_workspaces(username=username)
        return [ws.model_dump() for ws in workspaces]

    @mcp.tool(
        name="swanlab_get_workspace",
        description="Get detailed information about a specific workspace. 获取指定工作空间的详细信息。",
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
            返回空间详情，包含名称、角色、类型和介绍信息。
        """
        workspace = await workspace_tools.get_workspace(username)
        return workspace.model_dump()
