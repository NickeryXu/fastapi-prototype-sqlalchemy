from pydantic import BaseModel
from datetime import datetime
from typing import List


# user
class UserBase(BaseModel):
    name: str
    is_admin: bool


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    salt: str = ""
    hashed_password: str = ""

    class Config:
        orm_mode = True


class UserList(BaseModel):
    data: List[User]
    total: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    id: int
    exp: datetime
