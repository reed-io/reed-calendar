from define.BaseErrorCode import BaseErrorCode
from define.ErrorCode import ErrorCode

class ReedCalendarErrorCode(BaseErrorCode):
    """
        0x00A0~0x00BF
    """
    APPID_NOT_FOUND = ErrorCode(code=0x00a0, message="app_id not found in the path")
    APPID_NOT_CONFIGURED = ErrorCode(code=0x00a1, message="app_id not configured yet")
    APPID_CONFIG_EMPTY = ErrorCode(code=0x00a2, message="app_id configurations is empty")
    CHECK_TIMES_INVALIDATE = ErrorCode(code=0x00a3, message="check_time format is invalidate, array expect")
    CHECK_TIMES_ITEM_INVALIDATE = ErrorCode(code=0x00a4, message="item format in check_time format is invalidate, MM:SS expect")
    IMPORTANT_DAYS_INVALIDATE = ErrorCode(code=0x00a5, message="important_days format is invalidate, array expect")
    IMPORTANT_DAYS_ITEM_INVALIDATE = ErrorCode(code=0x00a6, message="item format in important_days is invalidate, json object expect")
    IMPORTANT_DAYS_ITEM_TYPE_EMPTY = ErrorCode(code=0x00a7, message="item type in important_days is empty")
    IMPORTANT_DAYS_ITEM_TYPE_ERROR = ErrorCode(code=0x00a8, message="item type in important_days should within[normal, week, lunar]")
    IMPORTANT_DAYS_ITEM_KEY_EMPTY = ErrorCode(code=0x00a9, message="item key in important_days is empty")
    IMPORTANT_DAYS_ITEM_VALUE_ERROR = ErrorCode(code=0x00aa, message="item value format in important_days invalidate, should be number and connect by '-'")
    IMPORTANT_DAYS_ITEM_VALUE_EMPTY = ErrorCode(code=0x00ab, message="item value in important_days is empty")
    YEAR_DATA_LENGTH_ERROR = ErrorCode(code=0x00ac, message="year data length is invalidate")
    YEAR_DATA_VALUE_ERROR = ErrorCode(code=0x00ad, message="year data value is invalidate")
    APPID_ALREADY_EXISTS = ErrorCode(code=0x00ae, message="app_id is already exists")
    DATE_INVALIDATE = ErrorCode(code=0x00af, message="invalidate date format, FYI->{%Y-%m-%d %H:%M:%S}")
    IS_WORK_INVALIDATE = ErrorCode(code=0x00b0, message="is_work is invalidate, only 0 or 1 accepted")
    DATE_DES_LIST_INVALIDATE = ErrorCode(code=0x00b1, message="date_des_list is invalidate, a string list expected")
    DATE_DES_LIST_ITEM_INVALIDATE = ErrorCode(code=0x00b2, message="item in date_des_list is invalidate, maybe not string or empty")
    YEAR_CONFIG_NOT_FOUND = ErrorCode(code=0x00b3, message="can not find year data")

    MONTH_CONFIG_NOT_FOUND = ErrorCode(code=0x00b4, message="can not find month data")
    MONTH_DATA_VALUE_ERROR = ErrorCode(code=0x00b6, message="month data value is invalidate")
    DAYS_REGION_EDGE_DATA_VALUE_ERROR = ErrorCode(code=0x00b7, message="days region edge value is error")




