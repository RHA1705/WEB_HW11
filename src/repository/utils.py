from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schema_user import RoleEnum, TokenData


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
SECRET_KEY = 'mysecretkey'

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def create_verification_token(email: str) -> str:
    """
    Create a verification token for email verification.

    Args:
        email (str): The email address for which to create the verification token.

    Returns:
        str: The generated JWT token for email verification.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=VERIFICATION_TOKEN_EXPIRE_HOURS
    )
    to_encode = {"exp": expire, "sub": email}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_verification_token(token: str) -> str | None:
    """
    Decode the verification token and extract the email address.

    Args:
        token (str): The JWT token to decode.

    Returns:
        str | None: The email address if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def create_access_token(data: dict):
    """
    Create an access token for authentication.

    Args:
        data (dict): The payload data to include in the token.

    Returns:
        str: The generated JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create a refresh token for renewing access tokens.

    Args:
        data (dict): The payload data to include in the refresh token.

    Returns:
        str: The generated JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData | None:
    """
    Decode the access token and extract the token data.

    Args:
        token (str): The JWT access token to decode.

    Returns:
        TokenData | None: The decoded token data if valid, or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_schema), db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user based on the provided access token.

    Args:
        token (str): The OAuth2 token provided by the client.
        db (Session): The SQLAlchemy session.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user = await repository_users.get_user_by_username(token_data.username, db)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    """
    Create an email verification token.

    Args:
        data (dict): The payload data to include in the token.

    Returns:
        str: The generated JWT token for email verification.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Extract the email from an email verification token.

    Args:
        token (str): The JWT email verification token.

    Returns:
        str: The email address extracted from the token.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Invalid token for email verification")


class RoleChecker:
    """
    A class for checking user roles.

    This class is used to enforce role-based access control (RBAC) for API endpoints.
    """
    def __init__(self, allowed_roles: list[RoleEnum]):
        """
        Initialize the RoleChecker with the allowed roles.

        Args:
            allowed_roles (list[RoleEnum]): A list of allowed roles for access.
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self, token: str = Depends(oauth2_schema), db: Session = Depends(get_db)
    ) -> User:
        """
        Check if the current user has one of the allowed roles.

        Args:
            token (str): The OAuth2 token provided by the client.
            db (Session): The SQLAlchemy session.

        Returns:
            User: The authenticated user if they have an allowed role.

        Raises:
            HTTPException: If the user does not have the required role.
        """
        user = await get_current_user(token, db)

        if user.role.name not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user
