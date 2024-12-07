from fastapi import APIRouter, status, Depends, HTTPException, Query
from src.schemas import ResponseContact, CreteContact
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository import contacts as repository_contacts
from typing import List


router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/search", response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def search_contacts(q: str = Query(None, description="Search string for name, second name, or email"), db: Session = Depends(get_db)):
    contact_s = await repository_contacts.search_contacts(q, db)
    return contact_s

@router.get('/birth', response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def get_contact_birthday(db: Session = Depends(get_db)):
    contacts = await repository_contacts.birthday(db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contacts

@router.get('/{contact_id}', response_model=ResponseContact, status_code=status.HTTP_200_OK)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contact

@router.get('/', response_model=List[ResponseContact], status_code=status.HTTP_200_OK)
async def get_contacts(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No contacts')
    return contacts



@router.put("/{contact_id}", response_model=ResponseContact)
async def update_contact(body: CreteContact, contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ResponseContact)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    tag = await repository_contacts.remove_contact(contact_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
@router.post('/', response_model=ResponseContact, status_code=status.HTTP_201_CREATED)
async def create_contact(body: CreteContact, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)
