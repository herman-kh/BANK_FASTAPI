from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    age: int


class Registration(BaseModel):
    message: str

class SuccsessfulRegistraionVerify(BaseModel):
    id: int
    username: str
    email: EmailStr
    status: str

class UserDataForAutorization(BaseModel):
    username: str
    email: str
    password: str
