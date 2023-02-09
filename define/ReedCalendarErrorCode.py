from define.BaseErrorCode import BaseErrorCode
from define.ErrorCode import ErrorCode

class ReedCalendarErrorCode(BaseErrorCode):
    """
        0x00A0~0x00AF
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






