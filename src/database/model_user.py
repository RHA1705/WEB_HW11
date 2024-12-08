from sqlalchemy import Column, Integer, String, Boolean, func, Table, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_name = Column(String(50), nullable=False)
#     email = Column(String(150), nullable=False, unique=True)
#     hashes_password = Column(String(50), nullable=False, unique=True)
#     # is_active = Column(Boolean, default=True)
#     contacts = relationship("Contact", back_populates="owner")
