import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, status, Depends, HTTPException, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.database.models import User
from src.repository.pass_utils import verify_password

from src.repository.utils import create_access_token, create_refresh_token, decode_verification_token, \
    get_email_from_token, get_current_user
from src.schema_user import UserResponse, UserCreate, Token, RequestEmail, UserBase

from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import users as repository_users
from src.services.email import send_email
from src.conf.config import settings

router = APIRouter(prefix='/users', tags=["users"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_create: UserCreate,
        db: Session = Depends(get_db)
):
    """
    Register a new user.

    Args:
        user_create (UserCreate): The user creation data.
        db (Session): The database session.

    Returns:
        UserResponse: The created user data.

    Raises:
        HTTPException: If the email is already registered.
    """
    user = await repository_users.get_user_by_email(user_create.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    user = await repository_users.create_user(user_create, db)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and provide access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): The form containing username and password.
        db (Session): The database session.

    Returns:
        Token: The generated access and refresh tokens.

    Raises:
        HTTPException: If authentication fails.
    """
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
    """
    Refresh the access token using a refresh token.

    Args:
        credentials (HTTPAuthorizationCredentials): The provided token.
        db (Session): The database session.

    Returns:
        Token: The new access and refresh tokens.

    Raises:
        HTTPException: If the token is invalid.
    """
    token = credentials.credentials
    email = await decode_verification_token(token)
    user = await repository_users.get_user_by_email(email, db)
    # if user.refresh_token != token:
    #     # await repository_users.update_token(user, None, db)
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": email})
    refresh_token_ = create_refresh_token(data={"sub": email})
    return Token(access_token=access_token, refresh_token=refresh_token_, token_type='bearer')


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address using a token.

    Args:
        token (str): The verification token.
        db (Session): The database session.

    Returns:
        dict: A message indicating the confirmation status.

    Raises:
        HTTPException: If the token is invalid or email confirmation fails.
    """
    email = await get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Request an email verification link.

    Args:
        body (RequestEmail): The email request data.
        background_tasks (BackgroundTasks): The background task handler.
        request (Request): The incoming request object.
        db (Session): The database session.

    Returns:
        dict | None: A message indicating the email request status.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.get("/me/", response_model=UserBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        UserBase: The user data.
    """
    return current_user


@router.patch('/avatar', response_model=UserBase)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    Update the avatar of the currently authenticated user.

    Args:
        file (UploadFile): The new avatar file.
        current_user (User): The currently authenticated user.
        db (Session): The database session.

    Returns:
        UserBase: The updated user data.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactApp/{current_user.user_name}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactApp/{current_user.user_name}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
