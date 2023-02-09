from pydantic import BaseModel
from define.ErrorCode import ErrorCode
from define.BaseErrorCode import BaseErrorCode

class ReedResult(BaseModel):
    code: int = BaseErrorCode.SUCCESS.code
    message: str = BaseErrorCode.SUCCESS.message
    data: object = None

    @classmethod
    def get(cls, error_code: ErrorCode, data=None):
        return cls(code=error_code.code, message=error_code.message, data=data)

    def __str__(self):
        return 'ReedResult{code=%s, message=%s, data=%s}' % (self.code, self.message, self.data)

    def standard_format(self):
        return self.json()
        # d = {'code': self.code, 'message': self.message, 'data': self.data}
        # return json.dumps(d)

