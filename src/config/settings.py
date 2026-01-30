"""Application settings using Pydantic Settings."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI
    openai_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/browserautomation.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Browser
    browser_headless: bool = True
    browser_channel: str = "chrome"  # "chrome", "msedge", "chromium", or empty for bundled

    @property
    def database_path(self) -> Path:
        """Get the SQLite database file path."""
        url = self.database_url
        if url.startswith("sqlite"):
            path = url.split("///")[-1]
            return Path(path)
        return Path("./data/browserautomation.db")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
