from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram
    bot_token: str

    # GostForge Backend
    backend_url: str = "http://backend:8080"

    # Internal API
    internal_api_key: str = "gostforge_internal_dev"

    # Mini App URL (auth portal served by frontend)
    mini_app_url: str = "http://localhost:3001"

    # Limits
    max_file_size_mb: int = 20

    model_config = {
        "env_prefix": "GOSTFORGE_",
        "env_file": ".env",
    }


settings = Settings()
