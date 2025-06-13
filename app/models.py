from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.dialects.mysql import LONGTEXT


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(String(50), nullable=True)
    email = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(100), nullable=True)
    password = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))


class ScrapedContacts(Base):
    __tablename__ = "scraped_contacts"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    site = Column(String(50), nullable=True)
    urls = Column(LONGTEXT, nullable=True)
    emails = Column(LONGTEXT, nullable=False)
    phones = Column(LONGTEXT, nullable=True)
    social_links = Column(LONGTEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()"))


