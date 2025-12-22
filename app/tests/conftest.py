from fastapi.testclient import TestClient
import pytest
from sqlmodel import create_engine, Session, SQLModel
import logging

from ..main import app
from ..config import settings
from ..database import get_session
from ..schemas import UserResponse
from ..oauth2 import create_access_token
from ..models import Post

TEST_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="user")
def test_user_1(client: TestClient):
    user = {"email": "user@user.com", "password": "123456789"}
    res = client.post("/users/", json=user)
    new_user = UserResponse(**res.json())
    assert new_user.email == "user@user.com"
    assert res.status_code == 201
    user["id"] = new_user.id
    return user


@pytest.fixture(name="user_2")
def test_user_2(client: TestClient):
    user = {"email": "user_2@user.com", "password": "123456789"}
    res = client.post("/users/", json=user)
    new_user = UserResponse(**res.json())
    assert new_user.email == "user_2@user.com"
    assert res.status_code == 201
    user["id"] = new_user.id
    return user


@pytest.fixture(name="authorized_user")
def authorized_user(client: TestClient, user: dict):
    token = create_access_token(data={"user_id": user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture(name="posts")
def test_posts(session: Session, user: dict, user_2: dict):
    post_data = [
        {"title": "first title", "content": "first content", "user_id": user["id"]},
        {"title": "second title", "content": "second content", "user_id": user["id"]},
        {"title": "third title", "content": "third content", "user_id": user["id"]},
        {"title": "fourth title", "content": "fourth content", "user_id": user_2["id"]},
    ]
    posts = [Post(**data) for data in post_data]
    session.add_all(posts)
    session.commit()

    for post in posts:
        session.refresh(post)

    return posts
