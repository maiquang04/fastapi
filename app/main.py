from . import models
from .database import SessionDep, create_db_and_tables
from .models import Post

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import time


create_db_and_tables()

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


@app.get("/sqlmodel")
def test_posts(session: SessionDep):
    return {"status": "success"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"post_detail": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    return {"data": updated_post}
