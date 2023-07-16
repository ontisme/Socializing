from pydantic import BaseModel


class AddTaskIn(BaseModel):
    profile_index: int
    script: str
    params: dict
