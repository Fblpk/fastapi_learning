

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=6, max_length=30)


class Token(BaseModel):
    access_token: str
    token_type: str


