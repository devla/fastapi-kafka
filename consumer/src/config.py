import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # FastAPI
    PROJECT_NAME: str
    DEBUG: bool

    # Kafka
    KAFKA_BROKERS: list
    KAFKA_GROUP_ID: str
    KAFKA_TOPICS: list
    KAFKA_REPLICATION_FACTOR: int
    KAFKA_PARTITIONS: int
    KAFKA_NUM_WORKERS: int = max(os.cpu_count() - 1, 1)

    # Database
    DB_ECHO: bool = False
    DB_FUTURE: bool = True
    DB_POOL_SIZE: int = 5

    # Postgres
    POSTGRES_HOST: str = "postgres-db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def KAFKA_CONFIG(self) -> list:
        return {
            "topics": self.KAFKA_TOPICS,
            "kafka_kwargs": {
                "bootstrap.servers": ",".join(self.KAFKA_BROKERS),
                "group.id": self.KAFKA_GROUP_ID,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            },
        }


@lru_cache
def get_settings():
    return Settings()
