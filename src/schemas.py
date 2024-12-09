from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


class CreteContact(BaseModel):
    name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=150)
    phone: str = Field(max_length=50)
    owner_id: int
    born_date: date


class ResponseContact(BaseModel):
    id: int
    name: str
    second_name: str
    email: EmailStr
    phone: str
    born_date: date
    crete_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True


