from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
import ast


class CreateUser(BaseModel):
    name: str = None
    email: EmailStr
    phone: str = None
    address: str = None
    password: str


class UserOut(BaseModel):
    id: int
    name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime


# ------------------------------------------------------------------------


class TokenData(BaseModel):
    id: int = None



# ------------------------------------------------------------------------

class SendEmail(BaseModel):
    email: List[EmailStr]


# ---------------------------------------------------------------------------


class SiteList(BaseModel):
    urls: List[str]


class ScraperOut(BaseModel):
    id: int
    url: str
    emails: str
    phones: str
    created_at: datetime

    # @field_validator("emails", mode="before")
    # def parse_emails_to_list(cls, v):
    #     if isinstance(v, str):
    #         try:
    #             return ast.literal_eval(v)
    #         except (SyntaxError, ValueError):
    #             raise ValueError("Invalid JSON string for email list")
    #     return v

    # @field_validator("phones", mode="before")
    # def parse_phones_to_list(cls, v):
    #     if isinstance(v, str):
    #         try:
    #             return ast.literal_eval(v)
    #         except (SyntaxError, ValueError):
    #             raise ValueError("Invalid JSON string for phone list")
    #     return v
