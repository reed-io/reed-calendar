# -*- coding: utf-8 -*-
import json
from datetime import datetime
from define.Solar import Solar
from utils.EnderUtil import TimeUtil
from utils.EnderUtil import StringUtil
from utils.HolidayUtil import HolidayUtil
from math import ceil

class EnderDay:

    def __init__(self, dt: datetime = datetime.now()):
        self.__dt = dt
        self.__solar = Solar.fromDate(self.__dt)
        self.__lunar = self.__solar.getLunar()
        self._version = 1.0


    def get_date(self):
        return self.__dt.date()

    def get_datetime(self):
        return self.__dt

    def get_year(self):
        return self.__solar.getYear()

    def get_month(self):
        return self.__solar.getMonth()

    def is_leap_year(self):
        return self.__solar.isLeapYear()

    def get_zodiac(self):
        return self.__lunar.getYearShengXiao()

    def get_year_lunar(self):
        return self.__lunar.getYear()

    def get_year_lunar_chinese(self):
        return self.__lunar.getYearInChinese()

    def get_year_ganzhi(self):
        return self.__lunar.getYearInGanZhi()

    def get_month_lunar(self):
        return self.__lunar.getMonth()

    def get_month_lunar_chinese(self):
        return self.__lunar.getMonthInChinese()

    def get_month_ganzhi(self):
        return self.__lunar.getMonthInGanZhi()

    def get_day_lunar(self):
        return self.__lunar.getDay()

    def get_day_lunar_chinese(self):
        return self.__lunar.getDayInChinese()

    def get_day_lunar_ganzhi(self):
        return self.__lunar.getDayInGanZhi()

    def get_weekday_idx(self) -> int:
        """
        获取当前是周几，0表示周日，1表示周一，6表示周六
        :return: 0,1,2,3,4,5,6
        """
        weekday = self.__dt.isoweekday()
        if weekday == 7:
            weekday = 0
        return weekday

    def get_weekday_chinese(self):
        return self.__solar.getWeekInChinese()

    def get_week_of_year(self):
        return TimeUtil.week_of_year(self.__dt)

    def get_day_of_year(self):
        return TimeUtil.day_of_year(self.__dt)

    def get_jie_qi(self):
        return self.__lunar.getJieQi()

    def get_astrological_sign(self):
        return self.__solar.getXingZuo()

    def get_solar_festivals(self):
        return self.__solar.getFestivals()

    def get_solar_other_festivals(self):
        return self.__solar.getOtherFestivals()

    def get_lunar_festivals(self):
        return self.__lunar.getFestivals()

    def get_lunar_other_festivals(self):
        return self.__lunar.getOtherFestivals()

    def get_festivals(self):
        return self.__solar.getFestivals()\
               + self.__solar.getOtherFestivals()\
               + self.__lunar.getFestivals()\
               + self.__lunar.getOtherFestivals()

    def is_weekend(self) -> bool:
        """
        :return: True if it's saturday or sunday
        """
        return True if self.get_weekday_idx() == 0 or self.get_weekday_idx() == 6 else False

    def is_work_day(self) -> bool:
        """
        :return: True if it is working day today
        """
        year = self.__dt.year
        for item in HolidayUtil._DATA_WORKDAY:
            if item["year"] == year:
                idx = TimeUtil.get_days_index(self.__dt)
                return True if item["data"][idx] == "0" else False
        return not self.is_weekend()

    def _private_important_days(self, important_days: list) -> list:
        private_important_days = list()
        for day in important_days:
            # day = eval(day)
            if day["type"] == "normal":
                key = "%d-%d" % (self.__dt.month, self.__dt.day)
                if day["key"] == key:
                    value_list = day["value"].split(",")
                    for value in value_list:
                        private_important_days.append(str(value).strip())
            if day["type"] == "week":
                key = "%d-%d-%d" % (self.__dt.month, int(ceil(self.__dt.day / 7.0)), self.get_weekday_idx())
                if day["key"] == key:
                    value_list = day["value"].split(",")
                    for value in value_list:
                        private_important_days.append(str(value).strip())
            if day["type"] == "lunar":
                key = "%d-%d" % (self.__lunar.getMonth(), self.__lunar.getDay())
                if day["key"] == key:
                    value_list = day["value"].split(",")
                    for value in value_list:
                        private_important_days.append(str(value).strip())
        return private_important_days

    def _private_is_work_day(self, private_calendar_data: str) -> bool:
        if StringUtil.isEmpty(private_calendar_data):
            return self.is_work_day()
        return True if private_calendar_data[TimeUtil.get_days_index(self.__dt)] == "0" else False

    def to_dict(self):
        return {
                    'datetime': self.get_datetime().__str__(),
                    'date': self.get_date().__str__(),
                    'is_leap_year': self.is_leap_year(),
                    'zodiac': self.get_zodiac(),
                    'lunar_year': self.get_year_lunar(),
                    'lunar_year_chinese': self.get_year_lunar_chinese(),
                    'lunar_year_ganzhi': self.get_year_ganzhi(),
                    'lunar_month': self.get_month_lunar(),
                    'lunar_month_chinese': self.get_month_lunar_chinese(),
                    'lunar_month_ganzhi': self.get_month_ganzhi(),
                    'lunar_day': self.get_day_lunar(),
                    'lunar_day_chinese': self.get_day_lunar_chinese(),
                    'lunar_day_ganzhi': self.get_day_lunar_ganzhi(),
                    'day_of_week': self.get_weekday_idx(),
                    'day_of_week_chinese': self.get_weekday_chinese(),
                    'week_of_year': self.get_week_of_year(),
                    'day_of_year': self.get_day_of_year(),
                    'jie_qi': self.get_jie_qi(),
                    'astrological_sign': self.get_astrological_sign(),
                    'is_weekend': self.is_weekend(),
                    'is_work_day': self.is_work_day(),
                    'festivals': self.get_festivals(),
                    'solar_festivals': self.get_solar_festivals(),
                    'solar_other_festivals': self.get_solar_other_festivals(),
                    'lunar_festivals': self.get_lunar_festivals(),
                    'lunar_other_festivals': self.get_lunar_other_festivals(),
                    'version:': self._version
                }

    def __format__(self, format_spec):
        return self.__str__()

    def __str__(self):
        return f"{{datetime:{self.get_datetime()}, date:{self.get_date()}, is_leap_year:{self.is_leap_year()}" \
               f", zodiac:{self.get_zodiac()}, lunar_year:{self.get_year_lunar()}" \
               f", lunar_year_chinese:{self.get_year_lunar_chinese()}, lunar_year_ganzhi:{self.get_year_ganzhi()}" \
               f", lunar_month:{self.get_month_lunar()}, lunar_month_chinese:{self.get_month_lunar_chinese()}" \
               f", lunar_month_ganzhi:{self.get_month_ganzhi()}, lunar_day:{self.get_day_lunar()}" \
               f", lunar_day_chinese:{self.get_day_lunar_chinese()}, lunar_day_ganzhi:{self.get_day_lunar_ganzhi()}" \
               f", day_of_week:{self.get_weekday_idx()}, day_of_week_chinese:{self.get_weekday_chinese()}" \
               f", week_of_year:{self.get_week_of_year()}, day_of_year:{self.get_day_of_year()}" \
               f", jie_qi:{self.get_jie_qi()}, astrological_sign:{self.get_astrological_sign()}" \
               f", is_weekend:{self.is_weekend()}, is_work_day:{self.is_work_day()}, festivals:{self.get_festivals()}" \
               f", version:{self._version}}}"
