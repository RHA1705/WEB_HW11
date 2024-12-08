from fastapi import APIRouter, status, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.repository.pass_utils import verify_password
from src.repository.users import create_user
from src.repository.utils import create_access_token, create_refresh_token, decode_verification_token
from src.schema_user import UserResponse, UserCreate, Token
from src.schemas import ResponseContact, CreteContact
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import users as repository_users
from typing import List

router = APIRouter(prefix='/users', tags=["users"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_create: UserCreate,
        # background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):

    user = await repository_users.get_user_by_email(user_create.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    user = await repository_users.create_user(user_create, db)
    # verification_token = create_verification_token(user.email)
    # verification_link = (
    #     f"http://localhost:8000/auth/verify-email?token={verification_token}"
    # )
    # template = env.get_template("verification_email.html")
    # email_body = template.render(verification_link=verification_link)
    # background_tasks.add_task(send_verification, user.email, email_body)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # user_repo = UserRepository(db)
    user = await repository_users.get_user_by_username(form_data.username, db)
    print(user)
    if not user or not verify_password(form_data.password, user.hashes_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.user_name})
    refresh_token = create_refresh_token(data={"sub": user.user_name})
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )

@router.get('/refresh_token', response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await decode_verification_token(token)
    user = await repository_users.get_user_by_email(email, db)
    # if user.refresh_token != token:
    #     # await repository_users.update_token(user, None, db)
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": email})
    refresh_token_ = create_refresh_token(data={"sub": email})
    # await repository_users.update_token(user, refresh_token, db)
    return Token(access_token=access_token, refresh_token=refresh_token_, token_type='bearer')
