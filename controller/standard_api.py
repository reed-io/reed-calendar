# -*- coding: utf-8 -*-
from define.ReedResult import ReedResult
from define.ReedCalendarErrorCode import ReedCalendarErrorCode as ErrorCode
from define.EnderDay import EnderDay
from utils.EnderUtil import TimeUtil
from fastapi import APIRouter
import logging

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


