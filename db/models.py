from sqlmodel import SQLModel, Field
from pydantic import field_validator

class UserBase(SQLModel):
    name: str = Field(min_length=5)
    email: str
    hashed_password: str = Field(min_length=8)

    @field_validator("email")
    def ensure_email_is_valid(cls, value):
        if "@" not in value:
            raise ValueError("Email is not valid, '@' is not included")
        return value 

class UserCreate(UserBase):
    pass

class User(UserBase, table=True):
    id: int = Field(primary_key=True, index=True)
    
class BookBase(SQLModel):
    name: str
    author: str
    borrowed: bool = False

class BookCreate(BookBase):
    pass

class Book(BookBase, table=True):
    id: int = Field(primary_key=True, index=True)
    borrowed_user_id: int | None = None
    
