"""Project related MCP tools."""

from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import OpenApi

from ..models import Project


class ProjectTools:
    """SwanLab Project management tools."""

    def __init__(self, api: OpenApi):
        self.api = api

    async def list_projects(self) -> List[Project]:
        """
        List all projects in the workspace.

        Returns:
            List of Project objects containing project information including:
            - cuid: Unique project identifier
            - name: Project name
            - description: Project description
            - visibility: PUBLIC or PRIVATE
            - createdAt/updatedAt: Timestamps
            - group: Workspace information
            - count: Statistics (experiments, contributors, etc.)
        """
        try:
            response = self.api.list_projects()
            # SwanLab API returns Project objects, convert to our Pydantic models
            projects = []
            for item in response.data:
                if hasattr(item, "model_dump"):
                    # If it's already a Pydantic model
                    projects.append(Project(**item.model_dump()))
                elif hasattr(item, "__dict__"):
                    # If it's a regular object with attributes
                    projects.append(Project(**item.__dict__))
                else:
                    # If it's a dict
                    projects.append(Project(**item))
            return projects
        except Exception as e:
            raise RuntimeError(f"Failed to list projects: {str(e)}") from e

    async def get_project(self, project: str) -> Project:
        """
        Get detailed information about a specific project by filtering from list.

        Args:
            project: Project name or CUID

        Returns:
            Project object with detailed information
        """
        try:
            # SwanLab API doesn't have get_project, so we filter from list_projects
            projects = await self.list_projects()
            for proj in projects:
                if proj.cuid == project or proj.name == project:
                    return proj
            raise ValueError(f"Project '{project}' not found")
        except Exception as e:
            raise RuntimeError(f"Failed to get project '{project}': {str(e)}") from e

    async def delete_project(self, project: str) -> str:
        """
        Delete a project from the workspace.

        Args:
            project: Project name or CUID to delete

        Returns:
            Success message
        """
        try:
            self.api.delete_project(project=project)
            return f"Successfully deleted project '{project}'"
        except Exception as e:
            raise RuntimeError(f"Failed to delete project '{project}': {str(e)}") from e


def register_project_tools(mcp: FastMCP, api: OpenApi) -> None:
    """
    Register project-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab OpenApi instance
    """
    project_tools = ProjectTools(api)

    @mcp.tool(
        name="swanlab_list_projects_in_a_workspace",
        description="List all projects in the workspace.",
        annotations=ToolAnnotations(
            title="List all projects in the workspace.",
            readOnlyHint=True,
        ),
    )
    async def list_projects() -> List[Dict[str, Any]]:
        """
        List all projects in the workspace.

        Returns:
            List of projects with details including name, description, visibility, statistics, etc.
        """
        projects = await project_tools.list_projects()
        return [project.model_dump() for project in projects]

    @mcp.tool(
        name="swanlab_get_a_specific_project",
        description="Get detailed information about a specific project.",
        annotations=ToolAnnotations(
            title="Get detailed information about a specific project.",
            readOnlyHint=True,
        ),
    )
    async def get_project(project: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.

        Args:
            project: Project name or CUID

        Returns:
            Project details including metadata and statistics.
        """
        project_obj = await project_tools.get_project(project)
        return project_obj.model_dump()

    @mcp.tool(
        name="swanlab_delete_a_project",
        description="Delete a project from the workspace. Warning: This action cannot be undone.",
        annotations=ToolAnnotations(
            title="Delete a project from the workspace. Warning: This action cannot be undone.",
            readOnlyHint=False,
        ),
    )
    async def delete_project(project: str) -> str:
        """
        Delete a project from the workspace.

        Args:
            project: Project name or CUID to delete

        Returns:
            Success message confirming deletion.
        """
        return await project_tools.delete_project(project)
