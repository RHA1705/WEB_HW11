from typing import List

from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from src.database.models import Contact
from src.schemas import CreteContact
from datetime import date, timedelta


async def search_contacts(query: str, user_id: int, db: Session):
    q = db.query(Contact).filter(Contact.owner_id == user_id, (Contact.name.ilike(query))
                                 | (Contact.second_name.ilike(query))
                                 | (Contact.email.ilike(query)))
    return q.all()


async def get_contact(contact_id: int, user_id: int, db: Session) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    return contact


async def update_contact(contact_id: int, user_id: int, body: Contact, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if contact:
        contact.name = body.name
        db.commit()
    return contact


async def remove_contact(contact_id: int, user_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts(user_id: int, db: Session) -> List[Contact]:
    contacts = db.query(Contact).filter(Contact.owner_id == user_id).all()
    return contacts


async def create_contact(body: CreteContact, user_id: int, db: Session) -> Contact:
    contact = Contact(name=body.name, second_name=body.second_name, email=body.email, phone=body.phone,
                      born_date=body.born_date, owner_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def birthday(user_id: int, db: Session):
    current_day = date.today()
    date_to = date.today() + timedelta(days=7)
    this_year = current_day.year
    next_year = current_day.year + 1
    contacts = db.query(Contact).filter(Contact.owner_id == user_id,
                                        or_(
                                            func.to_date(
                                                func.concat(func.to_char(Contact.born_date, "DDMM"), this_year),
                                                "DDMMYYYY").between(
                                                current_day, date_to),
                                            func.to_date(
                                                func.concat(func.to_char(Contact.born_date, "DDMM"), next_year),
                                                "DDMMYYYY").between(
                                                current_day, date_to)
                                        )
                                        ).all()
    return contacts
