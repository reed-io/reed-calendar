from define.ErrorCode import ErrorCode
class Father():
    SUCCESS = ErrorCode(code=0, message="test")
    def __setattr__(self, key, value):
        print("\t"+str(key)+"\t"+str(value))
        # raise Exception("aas")
        pass

class Son(Father):
    FAILED = ErrorCode(code=-1, message="ste")

from define.BaseErrorCode import BaseErrorCode
class TestErrorCode(Father):
    TEST_ERROR_CODE = ErrorCode(code=123, message="123123")


s = Son()
print(s.SUCCESS)
print(s.FAILED)
s.SUCCESS = ErrorCode(code=100, message="123123")
print(s.SUCCESS)

print(TestErrorCode.TEST_ERROR_CODE)
TestErrorCode.TEST_ERROR_CODE = ErrorCode(code=321, message="321312")
print(TestErrorCode.TEST_ERROR_CODE)
TestErrorCode.SUCCESS = ErrorCode(code=456, message="456456")
print(TestErrorCode.SUCCESS)
