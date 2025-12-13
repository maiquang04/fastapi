from fastapi import FastAPI
import psycopg
from psycopg.rows import dict_row
import time

from app.database import create_db_and_tables
from app.routers import post, user, auth

create_db_and_tables()

app = FastAPI()


while True:
    try:
        conn = psycopg.connect(
            "dbname=fastapi user=postgres password=123456789 host=localhost"
        )
        cursor = conn.cursor(row_factory=dict_row)
        print("✅ Connecting to database was successful")
        break
    except Exception as error:
        print("❌ Connecting to database failed")
        print(f"Error: {error}")
        time.sleep(3)


@app.get("/")
def read_root():
    return {"Hello": "Mate"}


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
