from pydantic import BaseModel


class CreateUserReq(BaseModel):
    email: str
    name: str
    password: str


class LoginUserReq(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    email: str
    name: str

    class Config:
        orm_mode = True
