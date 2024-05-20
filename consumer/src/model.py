from sqlalchemy import Column, text
from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import UUID, JSONB


class Message(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
        )
    )
    key: str | None = None
    value: dict | None = Field(sa_type=JSONB)
    headers: dict | None = Field(sa_type=JSONB)

    class Config:
        arbitrary_types_allowed = True
