import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class DatabaseConfig(BaseModel):
    host: str = os.getenv("DATABASE_HOST", "localhost")
    port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database: str = os.getenv("DATABASE_NAME", "")
    user: str = os.getenv("DATABASE_USER", "")
    password: str = os.getenv("DATABASE_PASSWORD", "")


class LLMConfig(BaseModel):
    api_key: str = os.getenv("LLM_API_KEY", "")
    api_base: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
    model: str = os.getenv("LLM_MODEL", "gpt-4")


class Config(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    max_retry_attempts: int = 3


config = Config()
