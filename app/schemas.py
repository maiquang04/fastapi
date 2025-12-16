from sqlmodel import SQLModel
from pydantic import EmailStr
from datetime import datetime
from typing import Literal


class PostBase(SQLModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    user: "UserResponse"


class PostWithVotesResponse(SQLModel):
    Post: PostResponse
    votes: int


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime


class Token(SQLModel):
    token: str
    token_type: str


class TokenData(SQLModel):
    id: int | None = None


class VoteCreate(SQLModel):
    post_id: int
    dir: Literal[0, 1]
