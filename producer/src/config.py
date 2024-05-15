import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        extra = "allow"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    # Kafka
    KAFKA_BROKERS: list
    KAFKA_TOPICS: list
    KAFKA_NUM_WORKERS: int = max(os.cpu_count() - 1, 1)

    @property
    def KAFKA_CONFIG(self) -> list:
        return {
            "kafka_kwargs": {
                "bootstrap.servers": ",".join(self.KAFKA_BROKERS),
            },
        }


@lru_cache
def get_settings():
    return Settings()
