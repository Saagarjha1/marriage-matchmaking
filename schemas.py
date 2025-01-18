from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    age: Optional[int] = None  # Optional field
    gender: Optional[str] = None  # Optional field
    email: EmailStr
    city: Optional[str] = None  # Optional field
    interests: Optional[List[str]] = []  # Optional field, default empty list

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)  # Enforcing minimum length for password

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)  # Minimum length for password
