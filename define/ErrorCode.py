from pydantic import BaseModel

class ErrorCode(BaseModel):
    code: int = 0
    message: str = '操作成功'

    @classmethod
    def get(cls, code, message):
        return cls(code=code, message=message)