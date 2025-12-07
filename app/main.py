from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


my_posts = [
    {"id": 1, "title": "title of post", "content": "content of post"},
    {"id": 2, "title": "favorite food", "content": "braised pork"},
]

while True:
    try:
        with psycopg.connect(
            "dbname=fastapi user=postgres password=123456789 host=localhost"
        ) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                print("✅ Connecting to database was successful")
                break
    except Exception as error:
        print("❌ Connecting to database failed")
        print(f"Error: {error}")
        time.sleep(3)


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


def find_post_index(id):
    for i, post in enumerate(my_posts):
        if post["id"] == id:
            return i


@app.get("/")
def read_root():
    return {"Hello": "Mate"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(int(id))
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return {"post_detail": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )
    my_posts.pop(index)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_post_index(id)

    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
