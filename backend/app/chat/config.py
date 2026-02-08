"""
Configuration for Chat Module (Phase III)

[FROM TASKS]: T001 - Project Setup Configuration

Loads environment variables for:
- OpenAI API configuration
- MCP Server configuration
- Chat service parameters
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    """Chat module configuration using Pydantic BaseSettings"""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview")
    openai_timeout: int = int(os.getenv("OPENAI_TIMEOUT", "30"))

    # MCP Server Configuration
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", "8500"))

    # Chat Service Configuration
    max_conversation_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    chat_request_timeout: int = int(os.getenv("CHAT_REQUEST_TIMEOUT", "30"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))

    # Rate Limiting
    rate_limit_requests_per_minute: int = int(
        os.getenv("RATE_LIMIT_RPM", "100")
    )

    # Environment
    environment: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global config instance
chat_config = ChatConfig()
