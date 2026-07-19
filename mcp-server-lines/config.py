from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Config to load environment variables from a .env file and ignore extra fields
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Configurations for the MCP server, loaded from environment variables
    MCP_HOST_LINES: str = Field(..., validation_alias="MCP_HOST")
    MCP_PORT_LINES: int = Field(..., validation_alias="MCP_PORT")


conf = Settings()