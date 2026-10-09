import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "dev"
    APP_SECRET_KEY: str = "dev-secret-key-support-copilot-2026-super-secure"
    CORS_ORIGINS: str = "http://localhost:4200,http://127.0.0.1:4200"

    # Generative Engine / LLM (Capgemini In-House Generative Engine)
    LLM_MODE: str = "fake"  # "engine" for live Generative Engine, "fake" for offline mock
    GENAI_BASE_URL: str = "https://openai.generative.engine.capgemini.com/v1"
    GENAI_API_KEY: str = "mock-key"
    GENAI_CHAT_MODEL: str = "gpt-4o"
    GENAI_EMBED_MODEL: str = "text-embedding-3-small"
    GENAI_TIMEOUT_SECONDS: int = 60
    GENAI_MAX_RETRIES: int = 3
    EMBEDDING_PROVIDER: str = "fake"  # "fake", "engine", "local"

    # Database
    # Default SQLite for instant offline run, or MSSQL connection string:
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/support_copilot.db"
    
    # MSSQL Settings (Windows Authentication / LocalDB or SQLEXPRESS)
    MSSQL_SERVER: str = r"(localdb)\MSSQLLocalDB"
    MSSQL_HOST: str = r"(localdb)\MSSQLLocalDB"
    MSSQL_PORT: int = 1433
    MSSQL_DB: str = "SUPPORT_COPILOT"
    MSSQL_USER: str = ""
    MSSQL_PASSWORD: str = ""
    MSSQL_USE_WINDOWS_AUTH: bool = True
    MSSQL_TRUST_SERVER_CERTIFICATE: bool = True
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    # Vector store (ChromaDB)
    CHROMA_PATH: str = "./data/chroma"
    CHROMA_COLLECTION: str = "kb_chunks"

    # Agent Behavior & Thresholds
    CLASSIFY_MIN_CONF: float = 0.6
    CRITIC_PASS_SCORE: float = 0.8
    MAX_CRITIC_LOOPS: int = 3
    RETRIEVAL_TOP_K: int = 4
    RETRIEVAL_MIN_SCORE: float = 0.35
    REFUND_AUTO_LIMIT: float = 500.0
    MAX_LLM_CALLS_PER_RUN: int = 12

    # Auth
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_MINUTES: int = 60
    JWT_REFRESH_DAYS: int = 7

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def mssql_connection_string(self) -> str:
        """Constructs an aioodbc connection URL for Microsoft SQL Server."""
        if self.MSSQL_USE_WINDOWS_AUTH:
            return (
                f"mssql+aioodbc://@{self.MSSQL_SERVER}/{self.MSSQL_DB}"
                f"?driver={self.MSSQL_DRIVER.replace(' ', '+')}"
                f"&Trusted_Connection=yes&TrustServerCertificate=yes"
            )
        else:
            return (
                f"mssql+aioodbc://{self.MSSQL_USER}:{self.MSSQL_PASSWORD}@{self.MSSQL_HOST}:{self.MSSQL_PORT}/{self.MSSQL_DB}"
                f"?driver={self.MSSQL_DRIVER.replace(' ', '+')}"
                f"&TrustServerCertificate=yes"
            )

settings = Settings()
