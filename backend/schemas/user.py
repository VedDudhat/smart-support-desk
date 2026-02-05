from pydantic import BaseModel, EmailStr, field_validator
import re

class UserRegisterSchema(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

    @field_validator('name')
    @classmethod
    def name_must_be_alpha(cls, v):
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError('Name cannot contain numbers or special characters.')
        return v.strip()

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long.')
        return v

class UserLoginSchema(BaseModel):
    username: str
    password: str