from pydantic import BaseModel


class UserLoginIn(BaseModel):
    username: str
    password: str
