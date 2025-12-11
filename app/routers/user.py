from fastapi import HTTPException, status, APIRouter
from sqlmodel import select
from app import schemas, utils, models
from app.database import SessionDep

router = APIRouter(prefix="/users")


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, session: SessionDep):
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, session: SessionDep):
    user = session.get(models.User, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist",
        )

    return user
