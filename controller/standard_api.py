# -*- coding: utf-8 -*-
from define.ReedResult import ReedResult
from define.ReedCalendarErrorCode import ReedCalendarErrorCode as ErrorCode
from define.EnderDay import EnderDay
from utils.EnderUtil import TimeUtil
from fastapi import APIRouter
import logging
from utils.DateTimeUtil import DateTimeUtil
from utils.SolarUtil import SolarUtil
import datetime

standard = APIRouter()


@standard.get('/today', tags=["获取当天信息"])
async def today():
    try:
        td = EnderDay()
        result = ReedResult.get(ErrorCode.SUCCESS, td.to_dict())
        logging.debug(result)
        return result
    except Exception as e:
        logging.error(e.__str__(), e.__dict__)
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@standard.get('/{day}', tags=["获取指定日期信息"])
async def someday(day):
    try:
        d = EnderDay(TimeUtil.get_date(day))
        result = ReedResult.get(ErrorCode.SUCCESS, d.to_dict())
        logging.debug(result)
        return result
    except Exception as e:
        logging.error(e.__str__(), e.__dict__)
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@standard.get("/month/{beginDate}/{endDate}")
def month_calendar_begin_end(beginDate, endDate):
    first_date = TimeUtil.get_date(beginDate)
    last_date = TimeUtil.get_date(endDate)
    days = DateTimeUtil.getDaysBetweenDate(first_date, last_date) + 1
    datas = []
    for i in range(0, days):
        n = datetime.timedelta(days=i)
        date = first_date + n
        datas.append(EnderDay(date).to_dict())
    result = ReedResult.get(ErrorCode.SUCCESS, data=datas)
    return result


@standard.get("/month/{yearMonth}")
def month_calendar(yearMonth):
    year = int(str(yearMonth).split("-")[0])
    month = int(str(yearMonth).split("-")[1])
    # days = SolarUtil.getDaysOfMonth(int(year), int(month))
    month_first_date = DateTimeUtil.fromYmd(year, month, 1)
    first_date = SolarUtil.getWeekFirstDay(month_first_date)
    """获取本月最后一天"""
    # month_last_date = DateTimeUtil.fromYmd(year, month, days)
    # last_date = SolarUtil.getWeekLastDay(month_last_date)
    # days = DateTimeUtil.getDaysBetweenDate(first_date,last_date)+1
    # if days != 42:
    #     last_date = SolarUtil.getNextWeekLastDay(month_last_date)
    # days = DateTimeUtil.getDaysBetweenDate(first_date, last_date) + 1
    # firstEnderDay = EnderDay(first_date)
    # lastEnderDay = EnderDay(last_date)
    datas = []
    for i in range(0, 42):
        n = datetime.timedelta(days=i)
        date = first_date + n
        datas.append(EnderDay(date).to_dict())
    result = ReedResult.get(ErrorCode.SUCCESS, data=datas)
    return result
