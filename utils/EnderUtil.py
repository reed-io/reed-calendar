import json
import re
import time
from datetime import datetime
import calendar

import pytz

class StringUtil(object):
    @staticmethod
    def isJson(source: str) -> bool:
        try:
            json.loads(source)
        except ValueError as e:
            return False
        return True


    @staticmethod
    def isEmpty(source: str) -> bool:
        if type(source) == str and len(str(source).strip()) == 0:
            return True
        else:
            return False


    @staticmethod
    def isHttpUrl(url: str) -> bool:
        pattern = re.compile('https?://([\w]+\.)+[\w]+(/[\w./?%&=]*)?$')
        return re.match(pattern, url)!=None


class TimeUtil(object):
    month_days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    @staticmethod
    def now() -> str:
        return datetime.now()

    @staticmethod
    def today() -> datetime:
        return datetime.now()

    @staticmethod
    def get_date(Y_m_d: str) -> datetime:
        return datetime.strptime(Y_m_d, "%Y-%m-%d")

    @staticmethod
    def get_datetime(Y_m_d_blank_H_M_S: str) -> datetime:
        return datetime.strptime(Y_m_d_blank_H_M_S, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def unix_now() -> int:
        return int(round(time.time()*1000))

    @staticmethod
    def local_time_struct(timeStr: str) -> datetime:
        return time.localtime(int(timeStr) / 1000)

    @staticmethod
    def format_time_second(timeStr: str) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", TimeUtil.local_time_struct(timeStr))

    @staticmethod
    def format_time_milsecond(timeStr: str) -> str:
        milsecond = timeStr[-3:]
        return TimeUtil.format_time_second(timeStr) + ":" + milsecond

    @staticmethod
    def parse_time_second(timeStr: str) -> datetime:
        return datetime.strptime(TimeUtil.format_time_second(timeStr), "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_seconds(timeStr: str) -> int:
        return int(round(time.mktime(time.strptime(timeStr, "%Y-%m-%d %H:%M:%S"))))*1000

    @staticmethod
    def is_validate_timezone(timezone: str) -> bool:
        print(pytz.all_timezones)
        if not StringUtil.isEmpty(timezone):
            return timezone in pytz.all_timezones
        else:
            return False

    @staticmethod
    def is_validate_datetime(dt: str) -> bool:
        try:
            datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return False
        return True

    @staticmethod
    def is_leap_year(year: int) -> bool:
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            return True
        return False

    @staticmethod
    def day_of_year(dt: datetime) -> int:
        year = dt.year
        month = dt.month
        day = dt.day
        result = 0
        for idx in range(len(TimeUtil.month_days)):
            if month > idx+1:
                if not TimeUtil.is_leap_year(year) and idx == 1:
                    result += 28
                else:
                    result += TimeUtil.month_days[idx]
        return result+day

    @staticmethod
    def week_of_year(dt: datetime) -> int:
        return dt.isocalendar()[1]+1

    @staticmethod
    def month_minus_day(dt: datetime) -> str:
        return "{}-{}".format(dt.month, dt.day)


    @staticmethod
    def get_days_index(dt: datetime) -> int:
        idx = -1
        for mIdx in range(dt.month - 1):
            idx += TimeUtil.month_days[mIdx]
        idx += dt.day
        if not TimeUtil.is_leap_year(dt.year) and dt.month > 2:
            idx -= 1
        return idx



    # print(TimeUtil.now())
    # print(TimeUtil.unix_now())
    # print(datetime.timestamp(datetime.now()))
    # print(calendar.timegm(time.gmtime()))
    # print(TimeUtil.format_time_second(TimeUtil.unix_now()))

    # print(TimeUtil.is_validate_datetime("1500-12-11 11:11:11"))

# print(TimeUtil.local_time_struct(time.time()*1000))
# print(time.strptime("2022-08-24 16:12:55", "%Y-%m-%d %H:%M:%S"))
# print(time.mktime(time.strptime("2022-08-24 16:12:55", "%Y-%m-%d %H:%M:%S")))
# print(TimeUtil.get_seconds("2022-08-24 16:12:55"))
# print(TimeUtil.unix_now()
# print(TimeUtil.format_time_second("1661328775000"))
# print(TimeUtil.day_of_year(TimeUtil.today()))
# print(TimeUtil.week_of_year(TimeUtil.today()))
# print(TimeUtil.month_minus_day(TimeUtil.get_date("2022-05-03")))

# print(TimeUtil.get_days_index(TimeUtil.get_date("2024-3-8")))
