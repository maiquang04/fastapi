from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlmodel import SQLModel, Field, text


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(
        nullable=False, default=True, sa_column_kwargs={"server_default": text("TRUE")}
    )
    created_at: str = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
        ),
    )
