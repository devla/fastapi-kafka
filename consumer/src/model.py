from datetime import datetime
from sqlalchemy.orm import registry
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel, registry=registry()):
    pass


# @TODO Check if onupdate=datetime.utcnow is needed for updated_at field.
# I'm not sure what default_factory does.
class TimeStampMixin(SQLModel):
    created_at: datetime | None = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow, nullable=False)


# class TimestampModel(SQLModel):
#    created_at: datetime = Field(
#        default_factory=datetime.utcnow,
#        nullable=False,
#        sa_column_kwargs={
#            "server_default": text("current_timestamp(0)")
#        }
#    )

#    updated_at: datetime = Field(
#        default_factory=datetime.utcnow,
#        nullable=False,
#        sa_column_kwargs={
#            "server_default": text("current_timestamp(0)"),
#            "onupdate": text("current_timestamp(0)")
#        }
#    )


# Load models:
# from src.auth.models import *  # noqa
