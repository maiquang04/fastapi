from fastapi.testclient import TestClient
import pytest

from ..schemas import Token
from ..oauth2 import decode_token


def test_root(client: TestClient):
    res = client.get("/")
    assert res.json().get("message") == "Hello World!"
    assert res.status_code == 200


def test_login(client: TestClient, user: dict):
    res = client.post(
        "/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    login_res = Token(**res.json())
    id = decode_token(login_res.token)
    assert id == user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrong_email", "123456789", 403),
        ("user@user.com", "wrong_password", 403),
        ("wrong_email", "wrong_password", 403),
        (None, "123456789", 422),
        ("user@user.com", None, 422),
    ],
)
def test_incorrect_login(client: TestClient, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    # assert res.json().get("detail") == "Invalid credentials"
