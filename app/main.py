from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
import time

from app.database import create_db_and_tables
from app.routers import post, user, auth

create_db_and_tables()

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "Mate"}


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
