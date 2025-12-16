from typing import List, Optional
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlmodel import ForeignKey, SQLModel, Field, text, Relationship
from datetime import datetime


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(
        nullable=False, default=True, sa_column_kwargs={"server_default": text("TRUE")}
    )
    created_at: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
        ),
    )

    user_id: int = Field(
        sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    user: Optional["User"] = Relationship(back_populates="posts")


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
        ),
    )

    posts: List[Post] = Relationship(back_populates="user")


class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    post_id: int = Field(foreign_key="posts.id", primary_key=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="users.id", primary_key=True, ondelete="CASCADE")
