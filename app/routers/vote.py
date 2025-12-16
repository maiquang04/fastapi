from fastapi import status, APIRouter, Depends, HTTPException
from sqlmodel import select

from .. import schemas, models, oauth2
from ..database import SessionDep

router = APIRouter(prefix="/votes", tags=["Vote"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def vote(
    vote: schemas.VoteCreate,
    session: SessionDep,
    user: models.User = Depends(oauth2.get_current_user),
):
    post = session.get(models.Post, vote.post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {vote.post_id} does not exist",
        )

    found_vote = session.exec(
        select(models.Vote)
        .where(models.Vote.post_id == vote.post_id)
        .where(models.Vote.user_id == user.id)
    ).first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {user.id} has already voted on post {vote.post_id}",
            )

        new_vote = models.Vote(post_id=vote.post_id, user_id=user.id)
        session.add(new_vote)
        session.commit()
        session.refresh(new_vote)

        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"vote does not exist"
            )

        session.delete(found_vote)
        session.commit()

        return {"message": "successfully deleted vote"}
