from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    user_id: str   # store MongoDB ObjectId as str
    username: str
    email: EmailStr
    hashed_password: str
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str   # plain text for registration only

class UserLogin(BaseModel):
    username: str
    password: str   # plain text for login only

# class UserResponse(BaseModel):
#     user_id:str
#     username: str
#     email: EmailStr
#     created_at: datetime
