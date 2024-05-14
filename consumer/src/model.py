from sqlalchemy import Column, text
from sqlalchemy.orm import registry
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB


class BaseModel(SQLModel, registry=registry()):
    pass


class Message(BaseModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        )
    )
    key: str | None = Field(nullable=True)
    value: dict | None = Field(nullable=True, sa_type=JSONB)

    class Config:
        arbitrary_types_allowed = True
