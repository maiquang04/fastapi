from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from typing import Annotated

from app import schemas, models, utils, oauth2
from app.database import SessionDep

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = session.exec(
        select(models.User).filter(models.User.email == user_credentials.username)
    ).first()

    if not user and not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentails"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"token": access_token, "token_type": "bearer"}
