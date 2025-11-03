"""Workspace related MCP tools."""

from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import OpenApi


class WorkspaceTools:
    """SwanLab Workspace management tools."""

    def __init__(self, api: OpenApi):
        self.api = api

    async def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all workspaces accessible to the current user.

        Returns:
            List of workspace dictionaries containing:
            - name: Workspace name
            - username: Workspace username/identifier
            - role: User's role in the workspace (OWNER, MEMBER, etc.)
        """
        try:
            response = self.api.list_workspaces()
            return response.data
        except Exception as e:
            raise RuntimeError(f"Failed to list workspaces: {str(e)}") from e


def register_workspace_tools(mcp: FastMCP, api: OpenApi) -> None:
    """
    Register workspace-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab OpenApi instance
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
    async def list_workspaces() -> List[Dict[str, Any]]:
        """
        List all workspaces accessible to the current user.

        Returns:
            List of workspaces with their names, usernames, and user roles.
        """
        return await workspace_tools.list_workspaces()
