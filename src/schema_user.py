from enum import Enum
from pydantic import BaseModel, EmailStr


class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    avatar: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    hashes_password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    username: str | None = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr
