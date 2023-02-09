import logging
from define.ErrorCode import ErrorCode


class BaseErrorCode():
    SUCCESS = ErrorCode(code=0x0000, message="操作成功")  # 0
    UNKNOWN_ERROR = ErrorCode.get(-0x0001, "未知错误")  # -1
    REQUEST_VALIDATION_ERROR = ErrorCode.get(-0x009D, "请求数据错误")  # -99
    def __setattr__(self, key, value):
        logging.warning("*"*10+"Attention! Someone trying to change final value in ["+str(self.__class__)+"]@"/
                        +str(key)+" from "+str(self.__getattribute__(key))+" to "+str(value)+", failed ofcourse :-)")
        print("*"*10+"Attention! Someone trying to change final value in ["+str(self.__class__)+"]@"/
                        +str(key)+" from "+str(self.__getattribute__(key))+" to "+str(value)+", failed ofcourse :-)")
        raise Exception("illegal modify with ErrorCode")
        ...


