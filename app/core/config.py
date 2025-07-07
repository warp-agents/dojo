# my_llm_app/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys
    LLM7_IO_API_KEY: str
    OPENROUTER_API_KEY: str
    GOOGLE_API_KEY_EXT: str
    FIRECRAWL_API_KEY: str

    # LLM Defaults (can be overridden)
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.95
    DEFAULT_MIN_P: float = 0.01
    DEFAULT_REPEAT_PENALTY: float = 1.0
    DEFAULT_TOP_K: int = 64

    # Pydantic settings configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Create a single instance to be used across the application
settings = Settings()