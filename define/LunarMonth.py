# -*- coding: utf-8 -*-
from define import LunarYear
from utils import LunarUtil


class LunarMonth:
    """
    农历月
    """

    def __init__(self, lunar_year, lunar_month, day_count, first_julian_day):
        self.__year = lunar_year
        self.__month = lunar_month
        self.__dayCount = day_count
        self.__firstJulianDay = first_julian_day

    @staticmethod
    def fromYm(lunar_year, lunar_month):
        from . import LunarYear
        return LunarYear.fromYear(lunar_year).getMonth(lunar_month)

    def getYear(self):
        return self.__year

    def getMonth(self):
        return self.__month

    def isLeap(self):
        return self.__month < 0

    def getDayCount(self):
        return self.__dayCount

    def getFirstJulianDay(self):
        return self.__firstJulianDay


    def toString(self):
        return "%d年%s%s月(%d天)" % (self.__year, ("闰" if self.isLeap() else ""), LunarUtil.MONTH[abs(self.__month)], self.__dayCount)

    def __str__(self):
        return self.toString()

    def next(self, n):
        """
        获取往后推几个月的阴历月，如果要往前推，则月数用负数
        :param n: 月数
        :return: 阴历月
        """
        if 0 == n:
            return LunarMonth.fromYm(self.__year, self.__month)
        elif n > 0:
            rest = n
            ny = self.__year
            iy = ny
            im = self.__month
            index = 0
            months = LunarYear.fromYear(ny).getMonths()
            while True:
                size = len(months)
                for i in range(0, size):
                    m = months[i]
                    if m.getYear() == iy and m.getMonth() == im:
                        index = i
                        break
                more = size - index - 1
                if rest < more:
                    break
                rest -= more
                last_month = months[size - 1]
                iy = last_month.getYear()
                im = last_month.getMonth()
                ny += 1
                months = LunarYear.fromYear(ny).getMonths()
            return months[index + rest]
        else:
            rest = -n
            ny = self.__year
            iy = ny
            im = self.__month
            index = 0
            months = LunarYear.fromYear(ny).getMonths()
            while True:
                size = len(months)
                for i in range(0, size):
                    m = months[i]
                    if m.getYear() == iy and m.getMonth() == im:
                        index = i
                        break
                if rest <= index:
                    break
                rest -= index
                first_month = months[0]
                iy = first_month.getYear()
                im = first_month.getMonth()
                ny -= 1
                months = LunarYear.fromYear(ny).getMonths()
            return months[index - rest]
