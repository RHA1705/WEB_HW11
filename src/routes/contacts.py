from fastapi import APIRouter, status, Depends, HTTPException, Query
from fastapi_limiter.depends import RateLimiter

from src.schemas import ResponseContact, CreteContact
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import contacts as repository_contacts
from typing import List
from src.database.models import User
from src.repository.utils import get_current_user

router = APIRouter(prefix='/contacts', tags=["contacts"], dependencies=[Depends(get_current_user)])


@router.get("/search", response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def search_contacts(q: str = Query(None, description="Search string for name, second name, or email"),
                          db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user)):
    """
    Search for contacts by name, second name, or email.

    Args:
        q (str): Query string for the search.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[ResponseContact]: A list of matching contacts.
    """
    user_id = current_user.id
    contact_s = await repository_contacts.search_contacts(q, user_id, db)
    return contact_s


@router.get('/birth', response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def get_contact_birthday(db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Get contacts who have a birthday in the next 7 days.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[ResponseContact]: A list of contacts with upcoming birthdays.

    Raises:
        HTTPException: If no contacts with upcoming birthdays are found.
    """
    user_id = current_user.id
    contacts = await repository_contacts.birthday(user_id, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contacts


@router.get('/{contact_id}', response_model=ResponseContact, status_code=status.HTTP_200_OK)
async def get_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a specific contact by ID.

    Args:
        contact_id (int): The ID of the contact.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        ResponseContact: The retrieved contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contacts.get_contact(contact_id, user_id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contact


@router.get('/', response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def get_contacts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve all contacts for the current user.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        List[ResponseContact]: A list of the user's contacts.

    Raises:
        HTTPException: If no contacts are found.
    """
    user_id = current_user.id
    contacts = await repository_contacts.get_contacts(user_id, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contacts


@router.put("/{contact_id}", response_model=ResponseContact)
async def update_contact(body: CreteContact,
                         contact_id: int,
                         current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)
                         ):
    """
    Update a contact's details.

    Args:
        body (CreteContact): The updated contact data.
        contact_id (int): The ID of the contact to update.
        current_user (User): The currently authenticated user.
        db (Session): The database session.

    Returns:
        ResponseContact: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    user_id = current_user.id
    contact = await repository_contacts.update_contact(contact_id, user_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ResponseContact)
async def remove_contact(contact_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """
    Remove a contact by ID.

    Args:
        contact_id (int): The ID of the contact to remove.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        ResponseContact: The removed contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    user_id = current_user.id
    tag = await repository_contacts.remove_contact(contact_id, user_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post('/', response_model=ResponseContact, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: CreteContact,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """
    Create a new contact.

    Args:
        body (CreteContact): The contact data to create.
        db (Session): The database session.
        current_user (User): The currently authenticated user.

    Returns:
        ResponseContact: The created contact.
    """
    user_id = current_user.id
    return await repository_contacts.create_contact(body, user_id, db)
