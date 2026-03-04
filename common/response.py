from typing import Any

from fastapi.responses import JSONResponse


# 统一响应格式封装
class ResponseModel:
    """统一响应格式模型"""

    @staticmethod
    def success(data: Any = None, msg: str = "操作成功") -> JSONResponse:
        """成功响应"""
        return JSONResponse(
            status_code=200, content={"code": 200, "msg": msg, "data": data}
        )

    @staticmethod
    def error(msg: str = "操作失败", data: Any = None) -> JSONResponse:
        """错误响应"""
        return JSONResponse(
            status_code=200, content={"code": 400, "msg": msg, "data": data}
        )

    @staticmethod
    def server_error(msg: str = "服务器内部错误", data: Any = None) -> JSONResponse:
        """服务器错误响应"""
        return JSONResponse(
            status_code=500, content={"code": 500, "msg": msg, "data": data}
        )
