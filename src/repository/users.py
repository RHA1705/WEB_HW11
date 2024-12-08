from typing import List

from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from src.database.models import User
from src.repository.pass_utils import get_password_hash
from src.schema_user import UserCreate
from datetime import date, timedelta


async def create_user(body: UserCreate, db: Session) -> User:
    hashed_password = get_password_hash(body.hashes_password)
    user = User(user_name=body.user_name, email=body.email, hashes_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_user_by_email(email: str, db: Session):
    query = db.query(User).filter(User.email == email).first()
    # result = await self.session.execute(query)
    return query  # result.scalar_one_or_none()


async def get_user_by_username(username: str, db: Session):
    query = db.query(User).filter(User.user_name == username).first()
    # result = await self.session.execute(query)
    return query  # result.scalar_one_or_none()

