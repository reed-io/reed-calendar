from enum import Enum


class ReedConst(Enum):
    COMMON_YES = True
    KEY_IMPORTANT_DAYS = "important_days"
    KEY_FESTIVALS = "festivals"
    KEY_IS_WORK_DAY = "is_work_day"
    KEY_REDIS_APP_PREFIX = "calendar_"


# print(ReedConst.COMMON_YES.value)
