"""Configuration management for xianyu-auto-reply backend.

Loads and validates environment variables from .env file,
providing a centralized config object used throughout the app.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration loaded from environment variables."""

    # --- Server ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")

    # --- Xianyu / Alibaba ---
    XIANYU_COOKIE: str = os.getenv("XIANYU_COOKIE", "")
    XIANYU_USER_ID: str = os.getenv("XIANYU_USER_ID", "")

    # --- AI Provider ---
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # openai | ollama | custom
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Ollama (optional local LLM) ---
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    # --- Auto-reply behaviour ---
    AUTO_REPLY_ENABLED: bool = os.getenv("AUTO_REPLY_ENABLED", "true").lower() == "true"
    REPLY_DELAY_SECONDS: float = float(os.getenv("REPLY_DELAY_SECONDS", "1.5"))
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "你是一个闲鱼平台的智能客服助手，请根据商品信息和买家问题给出简洁、友好的回复。",
    )

    # --- Database (SQLite by default) ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./xianyu.db")

    # --- Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")  # None → stdout only

    # --- WebSocket heartbeat ---
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    WS_RECONNECT_INTERVAL: int = int(os.getenv("WS_RECONNECT_INTERVAL", "5"))

    def validate(self) -> None:
        """Raise ValueError for any critically missing configuration."""
        errors: list[str] = []

        if not self.XIANYU_COOKIE:
            errors.append("XIANYU_COOKIE is required but not set.")
        if not self.XIANYU_USER_ID:
            errors.append("XIANYU_USER_ID is required but not set.")

        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            errors.append(
                "OPENAI_API_KEY is required when AI_PROVIDER is 'openai'."
            )

        if self.SECRET_KEY == "change-me-in-production" and not self.DEBUG:
            errors.append(
                "SECRET_KEY must be changed from the default value in production."
            )

        if errors:
            raise ValueError(
                "Configuration errors found:\n  - " + "\n  - ".join(errors)
            )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Config host={self.HOST}:{self.PORT} "
            f"provider={self.AI_PROVIDER} "
            f"debug={self.DEBUG}>"
        )


# Singleton instance used throughout the application
config = Config()
