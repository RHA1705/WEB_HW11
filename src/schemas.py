from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator


class CreteContact(BaseModel):
    name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)
    email: EmailStr = Field(max_length=150)
    phone: str = Field(max_length=50)
    born_date: date

    # @field_validator("born_date")
    # def parse_birthdate(cls, value):
    #     return datetime.strptime(
    #         value,
    #         "%d.%m.%Y"
    #     ).date()



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
