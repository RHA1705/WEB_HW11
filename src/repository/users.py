from sqlalchemy.orm import Session
from src.database.models import User
from src.repository.pass_utils import get_password_hash
from src.schema_user import UserCreate


async def create_user(body: UserCreate, db: Session) -> User:
    """
    Create a new user with hashed password and save it to the database.

    Args:
       body (UserCreate): The data for the new user.
       db (Session): The SQLAlchemy session.

    Returns:
       User: The created user object.
    """
    hashed_password = get_password_hash(body.hashes_password)
    user = User(user_name=body.user_name, email=body.email, hashes_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_user_by_email(email: str, db: Session):
    """
    Retrieve a user by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The SQLAlchemy session.

    Returns:
        User | None: The user object if found, or None if not.
    """
    query = db.query(User).filter(User.email == email).first()
    return query


async def get_user_by_username(username: str, db: Session):
    """
    Retrieve a user by their username.

    Args:
        username (str): The username of the user to retrieve.
        db (Session): The SQLAlchemy session.

    Returns:
        User | None: The user object if found, or None if not.
    """
    query = db.query(User).filter(User.user_name == username).first()
    return query


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm a user's email address by setting the confirmed flag to True.

    Args:
        email (str): The email address of the user to confirm.
        db (Session): The SQLAlchemy session.

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update a user's avatar URL.

    Args:
        email (str): The email address of the user whose avatar is updated.
        url (str): The new avatar URL.
        db (Session): The SQLAlchemy session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
