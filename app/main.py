from . import models
from .database import SessionDep, create_db_and_tables
from .models import Post

from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
import time
from sqlmodel import select


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


@app.get("/posts")
def get_posts(session: SessionDep):
    posts = session.exec(select(models.Post)).all()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int, session: SessionDep):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    post = session.get(models.Post, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"post_detail": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, session: SessionDep):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return {"data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = session.get(models.Post, id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    session.delete(post)
    session.commit()


@app.put("/posts/{id}")
def update_post(id: int, post: Post, session: SessionDep):
    # cursor.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, str(id)),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()
    db_post = session.get(models.Post, id)

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)

    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return {"data": db_post}
