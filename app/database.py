from fastapi import Depends
from sqlmodel import create_engine, Session, SQLModel
from typing import Annotated

DATABASE_URL = "postgresql+psycopg://postgres:123456789@localhost:5432/fastapi"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
