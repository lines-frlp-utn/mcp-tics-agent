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
    MCP_HOST_OUTLOOK:   str = Field(..., validation_alias="MCP_HOST_OUTLOOK")
    MCP_PORT_OUTLOOK:   int = Field(..., validation_alias="MCP_PORT_OUTLOOK")

    # Configurations for the IMAP connection
    TENANT_ID:          str = Field(..., validation_alias="TENANT_ID")
    CLIENT_ID:          str = Field(..., validation_alias="CLIENT_ID")
    CLIENT_SECRET:      str = Field(..., validation_alias="CLIENT_SECRET")
    EMAIL_ACCOUNT:      str = Field(..., validation_alias="EMAIL_ACCOUNT")


conf = Settings()