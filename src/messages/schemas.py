from pydantic import BaseModel
from typing import Optional


class MessageReq(BaseModel):
    text: str


class MessageUpdate(BaseModel):
    text: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True
