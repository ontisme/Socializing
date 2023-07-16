from pydantic import BaseModel


class UserLoginIn(BaseModel):
    account: str
    password: str
