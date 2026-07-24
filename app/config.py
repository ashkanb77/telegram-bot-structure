import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    sync_database_url: str
    redis_url: str
    langchain_database_url: str
    bot_token: str
    llm_model_name: str
    chatbot_provider: str
    chatbot_base_url: str
    chatbot_api_key: str
    llm_temperature: float
    llm_max_retires: int
    admin_key: str
    admin_username: str
    admin_password: str
    access_token_lifetime_minutes: int
    refresh_token_lifetime: int
    secret_key: str
    algorithm: str = "HS256"
    timezone: datetime.timezone = datetime.timezone.utc
    free_plan_name: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
