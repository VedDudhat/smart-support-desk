from pydantic import BaseModel, EmailStr, field_validator,ConfigDict
import re
from typing import Optional


class CustomerCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    firstname: str
    lastname: Optional[str]
    email: EmailStr
    company: str
    phone: Optional[str] = None

    @field_validator('firstname','lastname')
    @classmethod
    def name_must_be_alpha(cls, v):
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError('Name cannot contain numbers or special characters.')
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v:
            # Basic validation: 7 to 15 digits, allows +, -, and space
            if not re.match(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$', v):
                raise ValueError('Invalid phone number format')
        return v

class CustomerUpdateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    company: str | None = None
    phone: str | None = None

    @field_validator('firstname','lastname')
    @classmethod
    def name_must_be_alpha(cls, v):
        if v and not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError('Name cannot contain numbers or symbols')
        return v

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v):
        if v:
            # Strict Email Regex: letters@domain.extension
            regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(regex, v):
                raise ValueError('Please enter a valid email address (e.g. name@company.com)')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$', v):
            raise ValueError('Invalid phone number format')
        return v