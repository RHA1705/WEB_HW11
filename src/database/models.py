from sqlalchemy import Column, Integer, String, Boolean, func, Table, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    second_name = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(50), nullable=False, unique=True)
    born_date = Column(Date, nullable=False)
    crete_at = Column(DateTime, default=func.now())
    update_at = Column(DateTime, default=func.now(), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashes_password = Column(String(200), nullable=False, unique=True)
    confirmed = Column(Boolean, default=False)
    # is_active = Column(Boolean, default=True)
    contacts = relationship("Contact", back_populates="owner")
    avatar = Column(String, nullable=True)

