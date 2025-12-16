from typing import List

from fastapi import HTTPException, status, APIRouter, Depends
from sqlmodel import select, func
from app import schemas, models, oauth2
from app.database import SessionDep

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", response_model=List[schemas.PostWithVotesResponse])
def get_posts(
    session: SessionDep,
    user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    stmt = (
        select(models.Post, func.count(models.Vote.user_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .where(models.Post.user_id == user.id)
        .where(models.Post.title.contains(search))
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
    )

    result = session.exec(stmt).all()
    return result


@router.get("/{id}", response_model=schemas.PostWithVotesResponse)
def get_post(
    id: int, session: SessionDep, user: models.User = Depends(oauth2.get_current_user)
):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    stmt = (
        select(models.Post, func.count(models.Vote.user_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .where(models.Post.id == id)
        .where(models.Post.user_id == user.id)
        .group_by(models.Post.id)
    )

    result = session.exec(stmt).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} not found",
        )
        # response.status_code = status.HTTP_404_NOT_FOUND
    return result


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse,
)
def create_post(
    post: schemas.PostCreate,
    session: SessionDep,
    user: models.User = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(user_id=user.id, **post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int, session: SessionDep, user: models.User = Depends(oauth2.get_current_user)
):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = session.get(models.Post, id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    session.delete(post)
    session.commit()


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    post: schemas.PostCreate,
    session: SessionDep,
    user: models.User = Depends(oauth2.get_current_user),
):
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

    if db_post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    for key, value in post.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)

    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    return db_post
