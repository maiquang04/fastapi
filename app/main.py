from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import post, user, auth, vote
from .config import settings

# create_db_and_tables()

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def read_root():
    return {"Hello": "Mate"}
