"""Experiment related MCP tools."""

from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from swanlab import OpenApi

from ..models import Experiment


class ExperimentTools:
    """SwanLab Experiment management tools."""

    def __init__(self, api: OpenApi):
        self.api = api

    async def list_experiments(self, project: str) -> List[Experiment]:
        """
        List all experiments in a project.

        Args:
            project: Project name or CUID

        Returns:
            List of Experiment objects containing:
            - cuid: Unique experiment identifier
            - name: Experiment name
            - description: Experiment description
            - state: RUNNING or FINISHED
            - show: Display status
            - createdAt/finishedAt: Timestamps
            - user: Creator information
            - profile: Experiment configuration
        """
        try:
            response = self.api.list_experiments(project=project)
            experiments = []
            for item in response.data:
                if hasattr(item, "model_dump"):
                    experiments.append(Experiment(**item.model_dump()))
                elif hasattr(item, "__dict__"):
                    experiments.append(Experiment(**item.__dict__))
                else:
                    experiments.append(Experiment(**item))
            return experiments
        except Exception as e:
            raise RuntimeError(f"Failed to list experiments for project '{project}': {str(e)}") from e

    async def get_experiment(self, project: str, exp_id: str) -> Experiment:
        """
        Get detailed information about a specific experiment.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID

        Returns:
            Experiment object with detailed information including profile data
        """
        try:
            response = self.api.get_experiment(project=project, exp_id=exp_id)
            item = response.data
            if hasattr(item, "model_dump"):
                return Experiment(**item.model_dump())
            elif hasattr(item, "__dict__"):
                return Experiment(**item.__dict__)
            else:
                return Experiment(**item)
        except Exception as e:
            raise RuntimeError(f"Failed to get experiment '{exp_id}' from project '{project}': {str(e)}") from e

    async def get_summary(self, project: str, exp_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for an experiment's metrics.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID

        Returns:
            Dictionary containing metric summaries with step, value, min, and max information.
            Example: {"loss": {"step": 47, "value": 0.19, "min": {...}, "max": {...}}}
        """
        try:
            response = self.api.get_summary(project=project, exp_id=exp_id)
            return response.data
        except Exception as e:
            raise RuntimeError(f"Failed to get summary for experiment '{exp_id}': {str(e)}") from e

    async def get_metrics(self, exp_id: str, keys: Union[str, List[str]]) -> Optional[Dict[str, Any]]:
        """
        Get metric data for an experiment.

        Args:
            exp_id: Experiment CUID
            keys: List of metric names to retrieve (e.g., ["loss", "acc"])

        Returns:
            Dictionary containing metric values indexed by step.
            Includes both values and timestamps for each metric.
        """
        try:
            response = self.api.get_metrics(exp_id=exp_id, keys=keys if isinstance(keys, list) else [keys])
            data = response.data
            if hasattr(data, "to_dict"):
                return data.to_dict()
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get metrics for experiment '{exp_id}': {str(e)}") from e

    async def delete_experiment(self, project: str, exp_id: str) -> str:
        """
        Delete an experiment from a project.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID to delete

        Returns:
            Success message
        """
        try:
            self.api.delete_experiment(project=project, exp_id=exp_id)
            return f"Successfully deleted experiment '{exp_id}' from project '{project}'"
        except Exception as e:
            raise RuntimeError(f"Failed to delete experiment '{exp_id}': {str(e)}") from e


def register_experiment_tools(mcp: FastMCP, api: OpenApi) -> None:
    """
    Register experiment-related MCP tools.

    Args:
        mcp: FastMCP server instance
        api: SwanLab OpenApi instance
    """
    experiment_tools = ExperimentTools(api)

    @mcp.tool(
        name="swanlab_list_experiments_in_a_project",
        description="List all experiments in a project.",
        annotations=ToolAnnotations(
            title="List all experiments in a project.",
            readOnlyHint=True,
        ),
    )
    async def list_experiments(project: str) -> List[Dict[str, Any]]:
        """
        List all experiments in a project.

        Args:
            project: Project name or CUID

        Returns:
            List of experiments with their names, states, descriptions, and metadata.
        """
        experiments = await experiment_tools.list_experiments(project)
        return [exp.model_dump() for exp in experiments]

    @mcp.tool(
        name="swanlab_get_a_specific_experiment",
        description="Get detailed information about a specific experiment in a project.",
        annotations=ToolAnnotations(
            title="Get detailed information about a specific experiment in a project.",
            readOnlyHint=True,
        ),
    )
    async def get_experiment(project: str, exp_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific experiment.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID

        Returns:
            Experiment details including profile data, configuration, and metadata.
        """
        experiment = await experiment_tools.get_experiment(project, exp_id)
        return experiment.model_dump()

    @mcp.tool(
        name="swanlab_get_summary_for_an_experiment",
        description="Get summary statistics for an experiment's metrics.",
        annotations=ToolAnnotations(
            title="Get summary statistics for an experiment's metrics.",
            readOnlyHint=True,
        ),
    )
    async def get_experiment_summary(project: str, exp_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for an experiment's metrics.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID

        Returns:
            Dictionary containing metric summaries with step, value, min, and max information.
        """
        return await experiment_tools.get_summary(project, exp_id)

    @mcp.tool(
        name="swanlab_get_metrics_for_an_experiment",
        description="Get metric data for an experiment.",
        annotations=ToolAnnotations(
            title="Get metric data for an experiment.",
            readOnlyHint=True,
        ),
    )
    async def get_experiment_metrics(exp_id: str, keys: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get metric data for an experiment.

        Args:
            exp_id: Experiment CUID
            keys: Optional list of metric names to retrieve (e.g., ["loss", "acc"]).
                  If not provided, all metrics will be returned.

        Returns:
            Dictionary containing metric values indexed by step, including timestamps.
        """
        return await experiment_tools.get_metrics(exp_id, keys)

    @mcp.tool(
        name="swanlab_delete_an_experiment",
        description="Delete an experiment from a project. Warning: This action cannot be undone.",
        annotations=ToolAnnotations(
            title="Delete an experiment from a project. Warning: This action cannot be undone.",
            readOnlyHint=False,
        ),
    )
    async def delete_experiment(project: str, exp_id: str) -> str:
        """
        Delete an experiment from a project.

        Args:
            project: Project name or CUID
            exp_id: Experiment CUID to delete

        Returns:
            Success message confirming deletion.
        """
        return await experiment_tools.delete_experiment(project, exp_id)
