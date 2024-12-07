from sqlalchemy import Column, Integer, String, Boolean, func, Table, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

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

