from fastapi.testclient import TestClient
import pytest

from ..schemas import PostResponse, PostWithVotesResponse
from ..models import Post


def test_get_all_posts(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.get("/posts/")
    [PostWithVotesResponse(**post) for post in res.json()]
    assert len(res.json()) == 3
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client: TestClient, posts: list[Post]):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client: TestClient, posts: list[Post]):
    res = client.get(f"/posts/{posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.get("/posts/8888")
    assert res.status_code == 404


def test_get_one_post(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.get(f"/posts/{posts[0].id}")
    post = PostWithVotesResponse(**res.json())
    assert res.status_code == 200
    assert post.Post.id == posts[0].id
    assert post.Post.title == posts[0].title
    assert post.Post.content == posts[0].content


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("aaaa", "bbbbb", True),
        ("cccc", "afsdfasdfasf", True),
        ("sadfasdf", "ddddd", True),
    ],
)
def test_create_post(
    authorized_user: TestClient, posts: list[Post], title, content, published
):
    res = authorized_user.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )
    created_post = PostResponse(**res.json())
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published


@pytest.mark.parametrize(
    "title, content",
    [
        ("aaaa", "bbbbb"),
        ("cccc", "afsdfasdfasf"),
        ("sadfasdf", "ddddd"),
    ],
)
def test_create_post_published_true(
    authorized_user: TestClient,
    posts: list[Post],
    title,
    content,
):
    res = authorized_user.post("/posts/", json={"title": title, "content": content})
    created_post = PostResponse(**res.json())
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == True


def test_unauthorized_user_delete_post(client: TestClient, posts: list[Post]):
    res = client.delete(f"/posts/{posts[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.delete(f"/posts/{posts[0].id}")
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.delete("/posts/8888")
    assert res.status_code == 404


def test_delete_other_user_post(authorized_user: TestClient, posts: list[Post]):
    res = authorized_user.delete(f"/posts/{posts[3].id}")
    assert res.status_code == 403


def test_update_post(authorized_user: TestClient, posts: list[Post]):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": posts[0].published,
    }
    res = authorized_user.put(f"/posts/{posts[0].id}", json=data)
    updated_post = PostResponse(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_another_user_post(authorized_user: TestClient, posts: list[Post]):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": posts[3].published,
    }
    res = authorized_user.put(f"/posts/{posts[3].id}", json=data)
    assert res.status_code == 403


def test_update_another_user_post(authorized_user: TestClient, posts: list[Post]):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": posts[3].published,
    }
    res = authorized_user.put(f"/posts/{posts[3].id}", json=data)
    assert res.status_code == 403
