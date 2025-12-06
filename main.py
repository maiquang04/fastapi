from typing import Optional
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {"id": 1, "title": "title of post", "content": "content of post"},
    {"id": 2, "title": "favorite food", "content": "braised pork"},
]


@app.get("/")
def read_root():
    return {"Hello": "Mate"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/ posts")
def create_posts(new_post: Post):
    print(new_post.model_dump())
    return {"message": "successfully created post"}
