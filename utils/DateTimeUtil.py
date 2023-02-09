# -*- coding: utf-8 -*-
from datetime import datetime
from utils.SolarUtil import SolarUtil

class DateTimeUtil:
    """
    日期 时间 工具
    """
    def __init__(self):
        pass

    @staticmethod
    def fromYmdHms(year, month, day, hour, minute, second):
        return datetime(year, month, day, hour, minute, second, 0)

    @staticmethod
    def fromYmd(year, month, day):
        return DateTimeUtil.fromYmdHms(year, month, day, 0, 0, 0)

    @staticmethod
    def fromDate(date):
        return DateTimeUtil.fromYmdHms(date.year, date.month, date.day, date.hour, date.minute, date.second)

    @staticmethod
    def getDaysBetween(ay, am, ad, by, bm, bd):
        if ay == by:
            n = SolarUtil.getDaysInYear(by, bm, bd) - SolarUtil.getDaysInYear(ay, am, ad)
        elif ay > by:
            days = SolarUtil.getDaysOfYear(by) - SolarUtil.getDaysInYear(by, bm, bd)
            for i in range(by + 1, ay):
                days += SolarUtil.getDaysOfYear(i)
            days += SolarUtil.getDaysInYear(ay, am, ad)
            n = -days
        else:
            days = SolarUtil.getDaysOfYear(ay) - SolarUtil.getDaysInYear(ay, am, ad)
            for i in range(ay + 1, by):
                days += SolarUtil.getDaysOfYear(i)
            days += SolarUtil.getDaysInYear(by, bm, bd)
            n = days
        return n

    @staticmethod
    def getDaysBetweenDate(date0, date1):
        return DateTimeUtil.getDaysBetween(date0.year, date0.month, date0.day, date1.year, date1.month, date1.day)