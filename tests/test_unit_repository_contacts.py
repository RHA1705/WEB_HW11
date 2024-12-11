import unittest
from unittest.mock import MagicMock
from datetime import date
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import CreteContact
from src.repository.contacts import (
    search_contacts,
    get_contact,
    get_contacts,
    update_contact,
    remove_contact,
    create_contact,
    birthday,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]

        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(user_id=self.user.id, db=self.session)
        print(result)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = CreteContact(name="test", second_name="test note", email='email@example.com', phone='515590978',
                            owner_id=1, born_date=date.today())
        result = await create_contact(body=body, user_id=self.user.id, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertEqual(result, contact)

    #
    async def test_remove_note_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user_id=self.user.id, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = CreteContact(name="test_update", second_name='sn_upd', email='upd@example.com', phone='547896321',
                            owner_id=1, born_date=date.today())
        contact = Contact(name=body.name)
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, user_id=self.user.id, body=body, db=self.session)
        self.assertEqual(result, contact)


if __name__ == '__main__':
    unittest.main()
