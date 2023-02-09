# -*- coding: utf-8 -*-
from datetime import timedelta

from define.Solar import Solar
from define.JieQi import JieQi
from utils.LunarUtil import LunarUtil
from utils.SolarUtil import SolarUtil
from utils.DateTimeUtil import DateTimeUtil


class Lunar:
    """
    阴历日期
    """
    JIE_QI = ("冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪")
    JIE_QI_IN_USE = ("DA_XUE", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "DONG_ZHI", "XIAO_HAN", "DA_HAN", "LI_CHUN", "YU_SHUI", "JING_ZHE")

    def __init__(self, lunar_year, lunar_month, lunar_day, hour, minute, second):
        from define.LunarYear import LunarYear
        y = LunarYear.fromYear(lunar_year)
        m = y.getMonth(lunar_month)
        if m is None:
            raise Exception("wrong lunar year %d  month %d" % (lunar_year, lunar_month))
        if lunar_day < 1:
            raise Exception("lunar day must bigger than 0")
        days = m.getDayCount()
        if lunar_day > days:
            raise Exception("only %d days in lunar year %d month %d" % (days, lunar_year, lunar_month))
        self.__year = lunar_year
        self.__month = lunar_month
        self.__day = lunar_day
        self.__hour = hour
        self.__minute = minute
        self.__second = second
        self.__jieQi = {}
        self.__jieQiList = []
        noon = Solar.fromJulianDay(m.getFirstJulianDay() + lunar_day - 1)
        self.__solar = Solar.fromYmdHms(noon.getYear(), noon.getMonth(), noon.getDay(), hour, minute, second)
        if noon.getYear() != lunar_year:
            y = LunarYear.fromYear(noon.getYear())
        self.__compute(y)

    def __compute(self, y):
        self.__computeJieQi(y)
        self.__computeYear()
        self.__computeMonth()
        self.__computeDay()
        self.__computeTime()
        self.__computeWeek()

    def __computeJieQi(self, y):
        julian_days = y.getJieQiJulianDays()
        for i in range(0, len(Lunar.JIE_QI_IN_USE)):
            name = Lunar.JIE_QI_IN_USE[i]
            self.__jieQi[name] = Solar.fromJulianDay(julian_days[i])
            self.__jieQiList.append(name)

    def __computeYear(self):
        # 以正月初一开始
        offset = self.__year - 4
        year_gan_index = offset % 10
        year_zhi_index = offset % 12

        if year_gan_index < 0:
            year_gan_index += 10

        if year_zhi_index < 0:
            year_zhi_index += 12

        # 以立春作为新一年的开始的干支纪年
        g = year_gan_index
        z = year_zhi_index

        # 精确的干支纪年，以立春交接时刻为准
        g_exact = year_gan_index
        z_exact = year_zhi_index

        solar_year = self.__solar.getYear()
        solar_ymd = self.__solar.toYmd()
        solar_ymd_hms = self.__solar.toYmdHms()

        # 获取立春的阳历时刻
        li_chun = self.__jieQi["立春"]
        if li_chun.getYear() != solar_year:
            li_chun = self.__jieQi["LI_CHUN"]
        li_chun_ymd = li_chun.toYmd()
        li_chun_ymd_hms = li_chun.toYmdHms()

        # 阳历和阴历年份相同代表正月初一及以后
        if self.__year == solar_year:
            # 立春日期判断
            if solar_ymd < li_chun_ymd:
                g -= 1
                z -= 1
            # 立春交接时刻判断
            if solar_ymd_hms < li_chun_ymd_hms:
                g_exact -= 1
                z_exact -= 1
        elif self.__year < solar_year:
            if solar_ymd >= li_chun_ymd:
                g += 1
                z += 1
            if solar_ymd_hms >= li_chun_ymd_hms:
                g_exact += 1
                z_exact += 1

        self.__yearGanIndex = year_gan_index
        self.__yearZhiIndex = year_zhi_index

        self.__yearGanIndexByLiChun = (g + 10 if g < 0 else g) % 10
        self.__yearZhiIndexByLiChun = (z + 12 if z < 0 else z) % 12

        self.__yearGanIndexExact = (g_exact + 10 if g_exact < 0 else g_exact) % 10
        self.__yearZhiIndexExact = (z_exact + 12 if z_exact < 0 else z_exact) % 12

    def __computeMonth(self):
        ymd = self.__solar.toYmd()
        time = self.__solar.toYmdHms()
        size = len(Lunar.JIE_QI_IN_USE)

        # 序号：大雪以前-3，大雪到小寒之间-2，小寒到立春之间-1，立春之后0
        index = -3
        start = None
        for i in range(0, size, 2):
            end = self.__jieQi[Lunar.JIE_QI_IN_USE[i]]
            symd = ymd if start is None else start.toYmd()
            if symd <= ymd < end.toYmd():
                break
            start = end
            index += 1
        # 干偏移值（以立春当天起算）
        g_offset = (((self.__yearGanIndexByLiChun + (1 if index < 0 else 0)) % 5 + 1) * 2) % 10
        self.__monthGanIndex = ((index + 10 if index < 0 else index) + g_offset) % 10
        self.__monthZhiIndex = ((index + 12 if index < 0 else index) + LunarUtil.BASE_MONTH_ZHI_INDEX) % 12

        index = -3
        start = None
        for i in range(0, size, 2):
            end = self.__jieQi[Lunar.JIE_QI_IN_USE[i]]
            stime = time if start is None else start.toYmdHms()
            if stime <= time < end.toYmdHms():
                break
            start = end
            index += 1
        # 干偏移值（以立春交接时刻起算）
        g_offset = (((self.__yearGanIndexExact + (1 if index < 0 else 0)) % 5 + 1) * 2) % 10
        self.__monthGanIndexExact = ((index + 10 if index < 0 else index) + g_offset) % 10
        self.__monthZhiIndexExact = ((index + 12 if index < 0 else index) + LunarUtil.BASE_MONTH_ZHI_INDEX) % 12

    def __computeDay(self):
        noon = Solar.fromYmdHms(self.__solar.getYear(), self.__solar.getMonth(), self.__solar.getDay(), 12, 0, 0)
        offset = int(noon.getJulianDay()) - 11
        day_gan_index = offset % 10
        day_zhi_index = offset % 12

        self.__dayGanIndex = day_gan_index
        self.__dayZhiIndex = day_zhi_index

        day_gan_exact = day_gan_index
        day_zhi_exact = day_zhi_index

        # 八字流派2，晚子时（夜子/子夜）日柱算当天
        self.__dayGanIndexExact2 = day_gan_exact
        self.__dayZhiIndexExact2 = day_zhi_exact

        # 八字流派1，晚子时（夜子/子夜）日柱算明天
        hm = ("0" if self.__hour < 10 else "") + str(self.__hour) + ":" + ("0" if self.__minute < 10 else "") + str(self.__minute)
        if "23:00" <= hm <= "23:59":
            day_gan_exact += 1
            if day_gan_exact >= 10:
                day_gan_exact -= 10
            day_zhi_exact += 1
            if day_zhi_exact >= 12:
                day_zhi_exact -= 12
        self.__dayGanIndexExact = day_gan_exact
        self.__dayZhiIndexExact = day_zhi_exact

    def __computeTime(self):
        time_zhi_index = LunarUtil.getTimeZhiIndex(("0" if self.__hour < 10 else "") + str(self.__hour) + ":" + ("0" if self.__minute < 10 else "") + str(self.__minute))
        self.__timeZhiIndex = time_zhi_index
        self.__timeGanIndex = (self.__dayGanIndexExact % 5 * 2 + time_zhi_index) % 10

    def __computeWeek(self):
        self.__weekIndex = self.__solar.getWeek()

    @staticmethod
    def fromYmdHms(lunar_year, lunar_month, lunar_day, hour, minute, second):
        return Lunar(lunar_year, lunar_month, lunar_day, hour, minute, second)

    @staticmethod
    def fromYmd(lunar_year, lunar_month, lunar_day):
        return Lunar(lunar_year, lunar_month, lunar_day, 0, 0, 0)

    @staticmethod
    def fromDate(date):
        from define.LunarYear import LunarYear
        year = 0
        month = 0
        day = 0
        solar = Solar.fromDate(date)
        current_year = solar.getYear()
        current_month = solar.getMonth()
        current_day = solar.getDay()
        ly = LunarYear.fromYear(current_year)
        for m in ly.getMonths():
            # 初一
            first_day = Solar.fromJulianDay(m.getFirstJulianDay())
            days = DateTimeUtil.getDaysBetween(first_day.getYear(), first_day.getMonth(), first_day.getDay(), current_year, current_month, current_day)
            if days < m.getDayCount():
                year = m.getYear()
                month = m.getMonth()
                day = days + 1
                break
        return Lunar(year, month, day, solar.getHour(), solar.getMinute(), solar.getSecond())

    def getYear(self):
        return self.__year

    def getMonth(self):
        return self.__month

    def getDay(self):
        return self.__day

    def getHour(self):
        return self.__hour

    def getMinute(self):
        return self.__minute

    def getSecond(self):
        return self.__second

    def getSolar(self):
        return self.__solar

    def getYearGan(self):
        return LunarUtil.GAN[self.__yearGanIndex + 1]

    def getYearGanByLiChun(self):
        return LunarUtil.GAN[self.__yearGanIndexByLiChun + 1]

    def getYearGanExact(self):
        return LunarUtil.GAN[self.__yearGanIndexExact + 1]

    def getYearZhi(self):
        return LunarUtil.ZHI[self.__yearZhiIndex + 1]

    def getYearZhiByLiChun(self):
        return LunarUtil.ZHI[self.__yearZhiIndexByLiChun + 1]

    def getYearZhiExact(self):
        return LunarUtil.ZHI[self.__yearZhiIndexExact + 1]

    def getYearInGanZhi(self):
        return self.getYearGan() + self.getYearZhi()

    def getYearInGanZhiByLiChun(self):
        return self.getYearGanByLiChun() + self.getYearZhiByLiChun()

    def getYearInGanZhiExact(self):
        return self.getYearGanExact() + self.getYearZhiExact()

    def getMonthGan(self):
        return LunarUtil.GAN[self.__monthGanIndex + 1]

    def getMonthGanExact(self):
        return LunarUtil.GAN[self.__monthGanIndexExact + 1]

    def getMonthZhi(self):
        return LunarUtil.ZHI[self.__monthZhiIndex + 1]

    def getMonthZhiExact(self):
        return LunarUtil.ZHI[self.__monthZhiIndexExact + 1]

    def getMonthInGanZhi(self):
        return self.getMonthGan() + self.getMonthZhi()

    def getMonthInGanZhiExact(self):
        return self.getMonthGanExact() + self.getMonthZhiExact()

    def getDayGan(self):
        return LunarUtil.GAN[self.__dayGanIndex + 1]

    def getDayGanExact(self):
        return LunarUtil.GAN[self.__dayGanIndexExact + 1]

    def getDayGanExact2(self):
        return LunarUtil.GAN[self.__dayGanIndexExact2 + 1]

    def getDayZhi(self):
        return LunarUtil.ZHI[self.__dayZhiIndex + 1]

    def getDayZhiExact(self):
        return LunarUtil.ZHI[self.__dayZhiIndexExact + 1]

    def getDayZhiExact2(self):
        return LunarUtil.ZHI[self.__dayZhiIndexExact2 + 1]

    def getDayInGanZhi(self):
        return self.getDayGan() + self.getDayZhi()

    def getDayInGanZhiExact(self):
        return self.getDayGanExact() + self.getDayZhiExact()

    def getDayInGanZhiExact2(self):
        return self.getDayGanExact2() + self.getDayZhiExact2()

    def getTimeGan(self):
        return LunarUtil.GAN[self.__timeGanIndex + 1]

    def getTimeZhi(self):
        return LunarUtil.ZHI[self.__timeZhiIndex + 1]

    def getTimeInGanZhi(self):
        return self.getTimeGan() + self.getTimeZhi()

    def getYearShengXiao(self):
        return LunarUtil.SHENGXIAO[self.__yearZhiIndex + 1]

    def getYearShengXiaoByLiChun(self):
        return LunarUtil.SHENGXIAO[self.__yearZhiIndexByLiChun + 1]

    def getYearShengXiaoExact(self):
        return LunarUtil.SHENGXIAO[self.__yearZhiIndexExact + 1]

    def getMonthShengXiao(self):
        return LunarUtil.SHENGXIAO[self.__monthZhiIndex + 1]

    def getMonthShengXiaoExact(self):
        return LunarUtil.SHENGXIAO[self.__monthZhiIndexExact + 1]

    def getDayShengXiao(self):
        return LunarUtil.SHENGXIAO[self.__dayZhiIndex + 1]

    def getTimeShengXiao(self):
        return LunarUtil.SHENGXIAO[self.__timeZhiIndex + 1]

    def getYearInChinese(self):
        y = str(self.__year)
        s = ""
        for i in range(0, len(y)):
            s += LunarUtil.NUMBER[ord(y[i]) - 48]
        return s

    def getMonthInChinese(self):
        month = self.__month
        return ("闰" if month < 0 else "") + LunarUtil.MONTH[abs(month)]

    def getDayInChinese(self):
        return LunarUtil.DAY[self.__day]

    def getSeason(self):
        return LunarUtil.SEASON[abs(self.__month)]

    @staticmethod
    def __convertJieQi(name):
        jq = name
        if "DONG_ZHI" == jq:
            jq = "冬至"
        elif "DA_HAN" == jq:
            jq = "大寒"
        elif "XIAO_HAN" == jq:
            jq = "小寒"
        elif "LI_CHUN" == jq:
            jq = "立春"
        elif "DA_XUE" == jq:
            jq = "大雪"
        elif "YU_SHUI" == jq:
            jq = "雨水"
        elif "JING_ZHE" == jq:
            jq = "惊蛰"
        return jq

    def getJie(self):
        for i in range(0, len(Lunar.JIE_QI_IN_USE), 2):
            key = Lunar.JIE_QI_IN_USE[i]
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return self.__convertJieQi(key)
        return ""

    def getQi(self):
        for i in range(1, len(Lunar.JIE_QI_IN_USE), 2):
            key = Lunar.JIE_QI_IN_USE[i]
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return self.__convertJieQi(key)
        return ""

    def getWeek(self):
        return self.__weekIndex

    def getWeekInChinese(self):
        return SolarUtil.WEEK[self.getWeek()]

    def getFestivals(self):
        fs = []
        md = "%d-%d" % (self.__month, self.__day)
        if md in LunarUtil.FESTIVAL:
            fs.append(LunarUtil.FESTIVAL[md])
        if abs(self.__month) == 12 and self.__day >= 29 and self.__year != self.next(1).getYear():
            fs.append("除夕")
        return fs

    def getOtherFestivals(self):
        arr = []
        md = "%d-%d" % (self.__month, self.__day)
        if md in LunarUtil.OTHER_FESTIVAL:
            fs = LunarUtil.OTHER_FESTIVAL[md]
            for f in fs:
                arr.append(f)
        solar_ymd = self.__solar.toYmd()
        if solar_ymd == self.__jieQi["清明"].next(-1).toYmd():
            arr.append("寒食节")

        jq = self.__jieQi["立春"]
        offset = 4 - jq.getLunar().getDayGanIndex()
        if offset < 0:
            offset += 10
        if solar_ymd == jq.next(offset + 40).toYmd():
            arr.append("春社")

        jq = self.__jieQi["立秋"]
        offset = 4 - jq.getLunar().getDayGanIndex()
        if offset < 0:
            offset += 10
        if solar_ymd == jq.next(offset + 40).toYmd():
            arr.append("秋社")
        return arr

    def getJieQiTable(self):
        return self.__jieQi

    def getJieQiList(self):
        return self.__jieQiList

    def getTimeGanIndex(self):
        return self.__timeGanIndex

    def getTimeZhiIndex(self):
        return self.__timeZhiIndex

    def getDayGanIndex(self):
        return self.__dayGanIndex

    def getDayZhiIndex(self):
        return self.__dayZhiIndex

    def getDayGanIndexExact(self):
        return self.__dayGanIndexExact

    def getDayGanIndexExact2(self):
        return self.__dayGanIndexExact2

    def getDayZhiIndexExact(self):
        return self.__dayZhiIndexExact

    def getDayZhiIndexExact2(self):
        return self.__dayZhiIndexExact2

    def getMonthGanIndex(self):
        return self.__monthGanIndex

    def getMonthZhiIndex(self):
        return self.__monthZhiIndex

    def getMonthGanIndexExact(self):
        return self.__monthGanIndexExact

    def getMonthZhiIndexExact(self):
        return self.__monthZhiIndexExact

    def getYearGanIndex(self):
        return self.__yearGanIndex

    def getYearZhiIndex(self):
        return self.__yearZhiIndex

    def getYearGanIndexByLiChun(self):
        return self.__yearGanIndexByLiChun

    def getYearZhiIndexByLiChun(self):
        return self.__yearZhiIndexByLiChun

    def getYearGanIndexExact(self):
        return self.__yearGanIndexExact

    def getYearZhiIndexExact(self):
        return self.__yearZhiIndexExact

    def getNextJie(self, whole_day=False):
        """
        获取下一节（顺推的第一个节）
        :param whole_day: 是否按天计
        :return: 节气
        """
        conditions = []
        for i in range(0, int(len(Lunar.JIE_QI_IN_USE) / 2)):
            conditions.append(Lunar.JIE_QI_IN_USE[i * 2])
        return self.__getNearJieQi(True, conditions, whole_day)

    def getPrevJie(self, whole_day=False):
        """
        获取上一节（逆推的第一个节）
        :param whole_day: 是否按天计
        :return: 节气
        """
        conditions = []
        for i in range(0, int(len(Lunar.JIE_QI_IN_USE) / 2)):
            conditions.append(Lunar.JIE_QI_IN_USE[i * 2])
        return self.__getNearJieQi(False, conditions, whole_day)

    def getNextQi(self, whole_day=False):
        """
        获取下一气令（顺推的第一个气令）
        :param whole_day: 是否按天计
        :return: 节气
        """
        conditions = []
        for i in range(0, int(len(Lunar.JIE_QI_IN_USE) / 2)):
            conditions.append(Lunar.JIE_QI_IN_USE[i * 2 + 1])
        return self.__getNearJieQi(True, conditions, whole_day)

    def getPrevQi(self, whole_day=False):
        """
        获取上一气令（逆推的第一个气令）
        :param whole_day: 是否按天计
        :return: 节气
        """
        conditions = []
        for i in range(0, int(len(Lunar.JIE_QI_IN_USE) / 2)):
            conditions.append(Lunar.JIE_QI_IN_USE[i * 2 + 1])
        return self.__getNearJieQi(False, conditions, whole_day)

    def getNextJieQi(self, whole_day=False):
        """
        获取下一节气（顺推的第一个节气）
        :param whole_day: 是否按天计
        :return: 节气
        """
        return self.__getNearJieQi(True, None, whole_day)

    def getPrevJieQi(self, whole_day=False):
        """
        获取上一节气（逆推的第一个节气）
        :param whole_day: 是否按天计
        :return: 节气
        """
        return self.__getNearJieQi(False, None, whole_day)

    def __getNearJieQi(self, forward, conditions, whole_day):
        """
        获取最近的节气，如果未找到匹配的，返回null
        :param forward: 是否顺推，true为顺推，false为逆推
        :param conditions: 过滤条件，如果设置过滤条件，仅返回匹配该名称的
        :param whole_day: 是否按天计
        :return: 节气
        """
        name = None
        near = None
        filters = set()
        if conditions is not None:
            for cond in conditions:
                filters.add(cond)
        is_filter = len(filters) > 0
        today = self.__solar.toYmd() if whole_day else self.__solar.toYmdHms()
        for key in self.JIE_QI_IN_USE:
            jq = self.__convertJieQi(key)
            if is_filter and not filters.__contains__(jq):
                continue
            solar = self.__jieQi[key]
            day = solar.toYmd() if whole_day else solar.toYmdHms()
            if forward:
                if day < today:
                    continue
                if near is None:
                    name = jq
                    near = solar
                else:
                    near_day = near.toYmd() if whole_day else near.toYmdHms()
                    if day < near_day:
                        name = jq
                        near = solar
            else:
                if day > today:
                    continue
                if near is None:
                    name = jq
                    near = solar
                else:
                    near_day = near.toYmd() if whole_day else near.toYmdHms()
                    if day > near_day:
                        name = jq
                        near = solar
        if near is None:
            return None
        return JieQi(name, near)

    def getJieQi(self):
        """
        获取节气名称，如果无节气，返回空字符串
        :return: 节气名称
        """
        for key in self.__jieQi:
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return self.__convertJieQi(key)
        return ""

    def getCurrentJieQi(self):
        """
        获取当天节气对象，如果无节气，返回None
        :return: 节气对象
        """
        for key in self.__jieQi:
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return JieQi(self.__convertJieQi(key), self.__solar)
        return None

    def getCurrentJie(self):
        """
        获取当天节令对象，如果无节令，返回None
        :return: 节气对象
        """
        for i in range(0, len(Lunar.JIE_QI_IN_USE), 2):
            key = Lunar.JIE_QI_IN_USE[i]
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return JieQi(self.__convertJieQi(key), d)
        return None

    def getCurrentQi(self):
        """
        获取当天气令对象，如果无气令，返回None
        :return: 节气对象
        """
        for i in range(1, len(Lunar.JIE_QI_IN_USE), 2):
            key = Lunar.JIE_QI_IN_USE[i]
            d = self.__jieQi[key]
            if d.getYear() == self.__solar.getYear() and d.getMonth() == self.__solar.getMonth() and d.getDay() == self.__solar.getDay():
                return JieQi(self.__convertJieQi(key), d)
        return None

    def next(self, days):
        """
        获取往后推几天的农历日期，如果要往前推，则天数用负数
        :param days: 天数
        :return: 农历日期
        """
        return self.__solar.next(days).getLunar()

    def __str__(self):
        return self.toString()

    def toString(self):
        return "%s年%s月%s" % (self.getYearInChinese(), self.getMonthInChinese(), self.getDayInChinese())

    def toFullString(self):
        s = self.toString()
        s += " " + self.getYearInGanZhi() + "(" + self.getYearShengXiao() + ")年"
        s += " " + self.getMonthInGanZhi() + "(" + self.getMonthShengXiao() + ")月"
        s += " " + self.getDayInGanZhi() + "(" + self.getDayShengXiao() + ")日"
        s += " " + self.getTimeZhi() + "(" + self.getTimeShengXiao() + ")时" + "]"
        s += " 星期" + self.getWeekInChinese()
        for f in self.getFestivals():
            s += " (" + f + ")"
        for f in self.getOtherFestivals():
            s += " (" + f + ")"
        jq = self.getJieQi()
        if len(jq) > 0:
            s += " [" + jq + "]"
        return s

# print(Lunar(2022, 9, 12, 11,11,11).toFullString())