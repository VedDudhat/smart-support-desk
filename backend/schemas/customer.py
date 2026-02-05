from pydantic import BaseModel, EmailStr, field_validator,ConfigDict
import re

class CustomerCreateSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    email: EmailStr
    company: str

    @field_validator('name')
    @classmethod
    def name_must_be_alpha(cls, v):
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError('Name cannot contain numbers or special characters.')
        return v.strip()

class CustomerUpdateSchema(BaseModel):
    # This strips accidental spaces from the start/end of inputs
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    email: str | None = None # Use str here so we can apply our own strict regex
    company: str | None = None

    @field_validator('name')
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