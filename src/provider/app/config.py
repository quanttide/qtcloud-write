from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"


def get_settings() -> Settings:
    s = Settings()
    if not s.llm_api_key or s.llm_api_key == "your_deepseek_api_key_here":
        import os
        s.llm_api_key = os.environ.get("DEEPSEEK_API_KEY", s.llm_api_key)
    return s
