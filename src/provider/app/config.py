from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"


def get_settings() -> Settings:
    """懒加载，避免启动时就校验"""
    return Settings()
