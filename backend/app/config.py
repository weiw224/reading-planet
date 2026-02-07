from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "reading-planet"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    DATABASE_URL: str

    REDIS_URL: str = ""

    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    AI_API_URL: str = ""
    AI_API_KEY: str = ""
    AI_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
