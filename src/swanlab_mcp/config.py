"""Configuration management for SwanLab MCP Server."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SwanLabConfig(BaseSettings):
    """SwanLab MCP Server configuration settings.

    凭证解析优先级（由 swanlab >= 0.9.0 SDK 处理）：
    1. 此处的 SWANLAB_API_KEY / SWANLAB_HOST 环境变量
    2. 进程内登录态（swanlab.login）
    3. Settings 配置（.netrc 文件、swanlab.yaml、SWANLAB_ 前缀环境变量等）
    """

    # Authentication settings
    api_key: Optional[str] = Field(
        default=None,
        description="SwanLab API key for authentication; falls back to `swanlab login` credentials when unset",
        validation_alias="SWANLAB_API_KEY",
    )

    # Domain settings
    host: Optional[str] = Field(
        default=None,
        description="SwanLab server host URL; uses the logged-in host when unset",
        validation_alias="SWANLAB_HOST",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_config() -> SwanLabConfig:
    """
    Get the SwanLab configuration.

    Returns:
        SwanLabConfig instance with settings loaded from environment.
    """
    return SwanLabConfig()
