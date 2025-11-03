"""Configuration management for SwanLab MCP Server."""

from pydantic import Field
from pydantic_settings import BaseSettings

from .constants import DEFAULT_API_TIMEOUT_SECONDS, DEFAULT_SWANLAB_API_HOST, DEFAULT_SWANLAB_HOST


class SwanLabConfig(BaseSettings):
    """SwanLab MCP Server configuration settings."""

    # Authentication settings
    api_key: str | None = Field(
        default=None,
        description="SwanLab API key for authentication",
        validation_alias="SWANLAB_API_KEY",
    )

    # Domain settings
    main_domain: str = Field(
        default=DEFAULT_SWANLAB_HOST,
        description="SwanLab website domain",
        validation_alias="SWANLAB_HOST",
    )
    api_domain: str = Field(
        default=DEFAULT_SWANLAB_API_HOST,
        description="SwanLab API domain",
        validation_alias="SWANLAB_API_HOST",
    )

    # Request settings
    timeout: int = Field(
        default=DEFAULT_API_TIMEOUT_SECONDS,
        description="API request timeout in seconds",
        validation_alias="API_TIMEOUT",
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_config() -> SwanLabConfig:
    """
    Get the SwanLab configuration.

    Returns:
        SwanLabConfig instance with settings loaded from environment.

    Raises:
        ValueError: If required settings (like api_key) are not set.
    """
    config = SwanLabConfig()
    if not config.api_key:
        raise ValueError("SWANLAB_API_KEY environment variable must be set")
    return config
