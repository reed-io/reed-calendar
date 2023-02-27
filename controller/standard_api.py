# -*- coding: utf-8 -*-
from define.ReedResult import ReedResult
from define.ReedCalendarErrorCode import ReedCalendarErrorCode as ErrorCode
from define.EnderDay import EnderDay
from utils.EnderUtil import TimeUtil, StringUtil
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
async def someday(day: str):
    logging.debug(f"request param: day={day}")
    if StringUtil.isEmpty(day):
        logging.warning("path args: day is empty!")
        result = ReedResult.get(ErrorCode.MONTH_CONFIG_NOT_FOUND)
        return result
    if not TimeUtil.is_validate_date(day):
        logging.warning("invalidate day format")
        result = ReedResult.get(ErrorCode.DATE_INVALIDATE, day)
        return result
    try:
        d = EnderDay(TimeUtil.get_date(day))
        result = ReedResult.get(ErrorCode.SUCCESS, d.to_dict())
        logging.debug(result)
        return result
    except Exception as e:
        logging.error(e.__str__(), e.__dict__)
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@standard.get("/days/{beginDate}/{endDate}")
def month_calendar_begin_end(beginDate: str, endDate: str):
    logging.debug(f"request param: beginDate={beginDate},endDate={endDate}")
    if StringUtil.isEmpty(beginDate):
        logging.warning("path args: beginDate is empty!")
        result = ReedResult.get(ErrorCode.YEAR_CONFIG_NOT_FOUND)
        return result
    if StringUtil.isEmpty(endDate):
        logging.warning("path args: month is empty!")
        result = ReedResult.get(ErrorCode.MONTH_CONFIG_NOT_FOUND)
        return result
    if not TimeUtil.is_validate_date(beginDate):
        logging.warning("invalidate beginDate format")
        result = ReedResult.get(ErrorCode.DATE_INVALIDATE, beginDate)
        return result
    if not TimeUtil.is_validate_date(endDate):
        logging.warning("invalidate endDate format")
        result = ReedResult.get(ErrorCode.MONTH_DATA_VALUE_ERROR, endDate)
        return result
    first_date = TimeUtil.get_date(beginDate)
    last_date = TimeUtil.get_date(endDate)
    if first_date.timestamp() > last_date.timestamp():
        logging.warning("begin_date required large then end_date")
        result = ReedResult.get(ErrorCode.DAYS_REGION_EDGE_DATA_VALUE_ERROR, beginDate + "---->" + endDate)
        return result

    days = DateTimeUtil.getDaysBetweenDate(first_date, last_date) + 1
    datas = list()
    for i in range(0, days):
        n = datetime.timedelta(days=i)
        date = first_date + n
        datas.append(EnderDay(date).to_dict())
    result = ReedResult.get(ErrorCode.SUCCESS, data=datas)
    return result


@standard.get("/month/{year}/{month}")
def month_calendar(year: int, month: int):
    logging.debug(f"request param: year={year},month={month}")
    if year is None:
        logging.warning("path args: year is empty!")
        result = ReedResult.get(ErrorCode.YEAR_CONFIG_NOT_FOUND)
        return result
    if month is None:
        logging.warning("path args: month is empty!")
        result = ReedResult.get(ErrorCode.MONTH_CONFIG_NOT_FOUND)
        return result
    if not TimeUtil.is_validate_year(year):
        logging.warning("invalidate year format")
        result = ReedResult.get(ErrorCode.YEAR_DATA_VALUE_ERROR, year)
        return result
    if not TimeUtil.is_validate_month(month):
        logging.warning("invalidate month format")
        result = ReedResult.get(ErrorCode.MONTH_DATA_VALUE_ERROR, month)
        return result

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
    datas = list()
    for i in range(0, 42):
        n = datetime.timedelta(days=i)
        date = first_date + n
        datas.append(EnderDay(date).to_dict())
    result = ReedResult.get(ErrorCode.SUCCESS, data=datas)
    return result
