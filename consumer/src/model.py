import uuid
from sqlalchemy.orm import registry
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB


class BaseModel(SQLModel, registry=registry()):
    pass


class Message(BaseModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str | None = Field(nullable=True)
    value: dict | None = Field(nullable=True, sa_type=JSONB)
