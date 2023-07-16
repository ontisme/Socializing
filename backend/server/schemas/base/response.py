from typing import Union


def response_ok(message: str = "操作成功", data: Union[dict, list, str] = None):
    return {"code": 0, "data": data, "message": message}


def response_fail(message: str = "操作失敗", data: Union[dict, list, str] = None):
    return {"code": 400, "data": data, "message": message}
