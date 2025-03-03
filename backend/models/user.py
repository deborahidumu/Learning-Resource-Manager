from pydantic import BaseModel, field_validator, ValidationInfo
import re
from enum import Enum
from typing import List


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER =  'user'

class User(BaseModel):
    id: int
    username: str
    email: str | None = None
    roles: List[UserRole] = [UserRole.USER]

class UserWithPassword(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

    @field_validator('username', mode='before')
    def username_must_be_valid(cls, v: str):
        if not v or not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    @field_validator('confirm_password', mode='before')
    def passwords_match(cls, v, info: ValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @field_validator('email', mode='before')
    def email_must_be_valid(cls, v: str):
        if not v or not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError('Email must be a valid email address')
        return v
    
    @field_validator('password', mode='before')
    def password_must_be_valid(cls, v: str):
        if not v or len(v) < 5:
            raise ValueError('Password must be at least 5 characters long')
        return v
