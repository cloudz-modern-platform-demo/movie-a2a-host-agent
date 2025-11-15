"""Base settings for MCP and Gateway."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Settings for Application."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="ignore"
    )
    llm_model: str = "anthropic/claude-sonnet-4-5-20250929"


application_settings = ApplicationSettings()


class LoggerSettings(BaseSettings):
    """Settings for Logger."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="LOG_", env_file=".env", extra="ignore"
    )
    config_file: str = "logging.conf"
    level: str = "DEBUG"


logger_settings = LoggerSettings()
