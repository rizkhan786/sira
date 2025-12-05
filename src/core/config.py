"""Configuration management for SIRA using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API
    api_port: int = 8080
    api_host: str = "0.0.0.0"
    env: str = "development"
    
    # LLM
    llm_base_url: str = "http://sira-llm:11434"
    llm_model_general: str = "llama3:8b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # Reasoning
    max_reasoning_iterations: int = 3
    min_confidence_threshold: float = 0.7
    pattern_retrieval_count: int = 5
    fast_mode: bool = False  # Skip heavy reasoning for speed (set to False for full SIRA)
    
    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "sira"
    postgres_user: str = "sira"
    postgres_password: str
    
    chromadb_host: str = "chromadb"
    chromadb_port: int = 8000
    
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def chromadb_url(self) -> str:
        """Construct ChromaDB connection URL."""
        return f"http://{self.chromadb_host}:{self.chromadb_port}"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance."""
    return settings
