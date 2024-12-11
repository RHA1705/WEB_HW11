from typing import List

from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from src.database.models import Contact
from src.schemas import CreteContact
from datetime import date, timedelta


async def search_contacts(query: str, user_id: int, db: Session):
    """
    Search for contacts by a query string within a specific user's contacts.

    Args:
        query (str): The search query (matches name, second name, or email).
        user_id (int): The ID of the user whose contacts are searched.
        db (Session): The SQLAlchemy session.

    Returns:
        List[Contact]: A list of contacts matching the query.
    """
    q = db.query(Contact).filter(Contact.owner_id == user_id, (Contact.name.ilike(query))
                                 | (Contact.second_name.ilike(query))
                                 | (Contact.email.ilike(query)))
    return q.all()


async def get_contact(contact_id: int, user_id: int, db: Session) -> Contact:
    """
    Retrieve a specific contact by its ID for a given user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        user_id (int): The ID of the user who owns the contact.
        db (Session): The SQLAlchemy session.

    Returns:
        Contact: The retrieved contact object, or None if not found.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    return contact


async def update_contact(contact_id: int, user_id: int, body: Contact, db: Session) -> Contact | None:
    """
    Update the details of a contact for a specific user.

    Args:
        contact_id (int): The ID of the contact to update.
        user_id (int): The ID of the user who owns the contact.
        body (Contact): The updated contact data.
        db (Session): The SQLAlchemy session.

    Returns:
        Contact | None: The updated contact object, or None if the contact does not exist.
    """
    contact: object = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if contact:
        contact.name = body.name
        db.commit()
    return contact


async def remove_contact(contact_id: int, user_id: int, db: Session) -> Contact | None:
    """
    Remove a contact by its ID for a specific user.

    Args:
        contact_id (int): The ID of the contact to remove.
        user_id (int): The ID of the user who owns the contact.
        db (Session): The SQLAlchemy session.

    Returns:
        Contact | None: The removed contact object, or None if the contact does not exist.
    """
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_contacts(user_id: int, db: Session) -> List[Contact]:
    """
    Retrieve all contacts for a specific user.

    Args:
        user_id (int): The ID of the user whose contacts are retrieved.
        db (Session): The SQLAlchemy session.

    Returns:
        List[Contact]: A list of all contacts for the user.
    """
    contacts = db.query(Contact).filter(Contact.owner_id == user_id).all()
    return contacts


async def create_contact(body: CreteContact, user_id: int, db: Session) -> Contact:
    """
    Create a new contact for a specific user.

    Args:
        body (CreteContact): The contact data to create.
        user_id (int): The ID of the user who owns the new contact.
        db (Session): The SQLAlchemy session.

    Returns:
        Contact: The created contact object.
    """
    contact = Contact(name=body.name, second_name=body.second_name, email=body.email, phone=body.phone,
                      born_date=body.born_date, owner_id=user_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def birthday(user_id: int, db: Session):
    """
    Retrieve contacts with upcoming birthdays within the next week for a specific user.

    Args:
        user_id (int): The ID of the user whose contacts are checked.
        db (Session): The SQLAlchemy session.

    Returns:
        List[Contact]: A list of contacts with birthdays in the next 7 days.
    """
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
