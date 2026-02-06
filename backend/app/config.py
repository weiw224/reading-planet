from pydantic_settings import BaseSettings
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
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
