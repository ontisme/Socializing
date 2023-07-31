from fastapi import APIRouter

from server.schemas.base.response import response_ok
from server.schemas.user import UserLoginIn

router = APIRouter(prefix='/client', tags=['客戶端'])


@router.post("/users/login")
async def login(login_in: UserLoginIn):
    """登入指定平台"""
    data = {
        "token": "1234567890"
    }
    print("登入帳號：", login_in.username)
    return response_ok("登入成功", data)


@router.get("/users/info")
async def info():
    data = {
        "account": "admin",
        "roles": ["admin"],
    }
    return response_ok(data=data)


