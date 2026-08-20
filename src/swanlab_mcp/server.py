"""SwanLab MCP Server."""

from fastmcp import FastMCP

from .client import SwanLabClient
from .config import get_config
from .meta.info import get_server_name_with_version
from .tools import (
    register_metric_tools,
    register_project_tools,
    register_run_tools,
    register_user_tools,
    register_workspace_tools,
)


def create_mcp_server():
    # Load configuration (api_key/host optional; falls back to `swanlab login` credentials)
    config = get_config()

    # SwanLab OpenAPI client (swanlab >= 0.9.0): raw endpoints + shared SDK session
    client = SwanLabClient(api_key=config.api_key, host=config.host)

    # Initialize MCP server
    mcp = FastMCP(
        name=get_server_name_with_version(),
        instructions="""
        A Model Context Protocol (MCP) server for SwanLab - a collaborative machine learning experiment tracking platform.

        This server provides read-only tools built on the SwanLab OpenAPI HTTP layer (swanlab SDK >= 0.9.0) to:
        - Query the authenticated user profile and workspace metadata
        - Query project metadata and paginated project lists
        - Query paginated/filtered run (experiment) lists, run details, config, metadata and requirements
        - Discover metric keys (series), then fetch scalar metrics, summaries, medias and console logs

        Authentication: set SWANLAB_API_KEY (and optionally SWANLAB_HOST) in the environment,
        or rely on credentials stored by `swanlab login` (~/.swanlab/.netrc).
        """,
    )

    # Register all tools
    register_user_tools(mcp, client)
    register_workspace_tools(mcp, client)
    register_project_tools(mcp, client)
    register_run_tools(mcp, client)
    register_metric_tools(mcp, client)
    return mcp
