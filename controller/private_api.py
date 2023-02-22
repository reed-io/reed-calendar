# -*- coding: utf-8 -*-

from utils.EnderUtil import StringUtil
from utils.EnderUtil import TimeUtil
from define.ReedResult import ReedResult
from define.EnderDay import EnderDay
from define.ReedCalendarErrorCode import ReedCalendarErrorCode as ErrorCode
from fastapi import APIRouter, Request, Form

import json
import re
import logging

private = APIRouter()

time_pattern = re.compile("((([01]\\d)|(2[0-3]))|(\d)):[0-5]\\d(:[0-5]\\d)?")


@private.get('/{app_id}/today', tags=["获取当天信息"])
async def today(app_id, request: Request):
    redis_conn = request.app.state.redis
    logging.debug("app_id="+app_id)
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        key = "calendar_"+app_id
        exists = await redis_conn.exists(key)
        if not exists:
            logging.warning("can not find "+key+" in redis!")
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        td = EnderDay()
        _result = td.to_dict()
        important_days = await redis_conn.hget(key, "important_days")
        logging.debug("redis hget(important_days)="+important_days)
        print("redis", key, "important_days", important_days)
        important_days = json.loads(json.dumps(eval(important_days)))
        private_important_days = td._private_important_days(important_days)
        logging.debug("after handle private important_days="+str(private_important_days))
        print("private_important_days", private_important_days)
        _result["important_days"] = private_important_days
        _result["festivals"] = _result["festivals"]+private_important_days
        private_calendar_year_key = "year_"+str(td.get_datetime().year)
        hash_exists = await redis_conn.hexists(key, private_calendar_year_key)
        if hash_exists:
            private_calendar_year_data = await redis_conn.hget(key, private_calendar_year_key)
            print("private_calendar_year_data", private_calendar_year_data)
            _result["is_work_day"] = td._private_is_work_day(private_calendar_year_data)
        result = ReedResult.get(ErrorCode.SUCCESS, _result)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result

@private.get("/{app_id}/configuration", tags=["获取配置信息"])
async def get_configuration(app_id, request: Request):
    redis_conn = request.app.state.redis
    logging.debug("app_id=" + app_id)
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        key = "calendar_" + app_id
        exists = await redis_conn.exists(key)
        if not exists:
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        result = dict()
        result["app_id"] = app_id
        check_times = await redis_conn.hget(key, "check_times")
        check_times = json.loads(json.dumps(check_times))
        result["check_times"] = eval(check_times)
        important_days = await redis_conn.hget(key, "important_days")
        important_days = json.loads(json.dumps(important_days))
        result["important_days"] = eval(important_days)
        hkeys = await redis_conn.hkeys(key)
        for item in hkeys:
            if item.startswith("year_"):
                important_day = await redis_conn.hget(key, item)
                result[item[5:]] = important_day
        result = ReedResult.get(ErrorCode.SUCCESS, result)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result

@private.get('/{app_id}/{date}', tags=["获取指定日期信息"])
async def someday(app_id, date, request: Request):
    redis_conn = request.app.state.redis
    logging.debug("app_id=" + app_id)
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        if not TimeUtil.is_validate_datetime(date):
            logging.warning("invalidate date format")
            result = ReedResult.get(ErrorCode.DATE_INVALIDATE, date)
            return result

        key = "calendar_" + app_id
        exists = await redis_conn.exists(key)
        if not exists:
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        d = EnderDay(TimeUtil.get_date(date))
        _result = d.to_dict()
        important_days = await redis_conn.hget(key, "important_days")
        print("redis", key, "important_days", important_days)
        important_days = json.loads(json.dumps(eval(important_days)))
        private_important_days = d._private_important_days(important_days)
        print("private_important_days", private_important_days)
        _result["important_days"] = private_important_days
        _result["festivals"] = _result["festivals"] + private_important_days
        private_calendar_year_key = "year_" + str(d.get_datetime().year)
        hexists = await redis_conn.hexists(key, private_calendar_year_key)
        if hexists:
            private_calendar_year_data = await redis_conn.hget(key, private_calendar_year_key)
            print("private_calendar_year_data", private_calendar_year_data)
            _result["is_work_day"] = d._private_is_work_day(private_calendar_year_data)
        result = ReedResult.get(ErrorCode.SUCCESS, _result)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result

@private.api_route("/{app_id}/configuration", methods=["PUT", "POST"], tags=["创建或修改配置信息"])
async def post_put_configuration(app_id, request: Request, check_times=Form(),
                                 important_days=Form()):
    redis_conn = request.app.state.redis
    method = request.method
    logging.debug(method)
    logging.debug("app_id=" + app_id)
    app_id_key = "calendar_" + app_id
    try:
        params = await request.form()
        logging.debug("params="+str(params))
        year_data = list(filter(lambda year: len(year) == 4 and 1900 < eval(year) < 3000, params))
        print(app_id, check_times, important_days, year_data)
        if StringUtil.isEmpty(app_id):
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND, app_id)
            return result
        if (check_times is None or len(check_times) == 0) and (important_days is None or len(important_days) == 0)\
                and len(year_data) == 0:
            result = ReedResult.get(ErrorCode.APPID_CONFIG_EMPTY, app_id)
            return result

        app_id_exists = await redis_conn.exists(app_id_key)
        if method == "POST" and app_id_exists:
            logging.warning("app_id already exists!")
            result = ReedResult.get(ErrorCode.APPID_ALREADY_EXISTS, app_id)
            return result

        if check_times and len(check_times) > 0:
            check_times = eval(check_times)
            if type(check_times) != list:
                result = ReedResult.get(ErrorCode.CHECK_TIMES_INVALIDATE, str(check_times))
                return result
            check_time_list = list()
            for check_time in check_times:
                if re.match(time_pattern, check_time):
                    check_time_list.append(check_time)
                else:
                    result = ReedResult.get(ErrorCode.CHECK_TIMES_ITEM_INVALIDATE, check_time)
                    return result
            # await redis_conn.hset(app_id_key, "check_times", str(check_time_list))

        important_day_list = list()
        if important_days and len(important_days) > 0:
            important_days = eval(important_days)
            if type(check_times) != list:
                result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_INVALIDATE, str(important_days))
                return result
            for important_day in important_days:
                if type(important_day) != dict:
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_INVALIDATE, important_day)
                    return result
                important_day = dict(important_day)
                if important_day.get("type") is None or StringUtil.isEmpty(important_day["type"]):
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_TYPE_EMPTY, important_day)
                    return result
                type_value = important_day["type"]
                if str.lower(type_value) not in ("normal", "week", "lunar"):
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_TYPE_ERROR, important_day)
                    return result

                if important_day.get("key") is None or StringUtil.isEmpty(important_day["key"]):
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_KEY_EMPTY, important_day)
                    return result
                key_value = str(important_day["key"])
                key_value_list = key_value.split("-")
                if len(key_value_list) <= 1:
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_VALUE_ERROR, important_day)
                    return result
                for i in key_value_list:
                    if type(eval(i)) is not int:
                        result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_VALUE_ERROR, important_day)
                        return result

                if important_day.get("value") is None or StringUtil.isEmpty(important_day["value"]):
                    result = ReedResult.get(ErrorCode.IMPORTANT_DAYS_ITEM_VALUE_EMPTY, important_day)
                    return result

                important_day_list.append(important_day)
                # await redis_conn.hset(app_id_key, "important_days", str(important_day_list))

        year_data_dict = dict()
        for year in year_data:
            _data = str(params[year])
            if len(_data) != 365 and len(_data) != 366:
                result = ReedResult.get(ErrorCode.YEAR_DATA_LENGTH_ERROR, (year, _data))
                return result
            for n in _data:
                if n != "0" and n != "1":
                    result = ReedResult.get(ErrorCode.YEAR_DATA_VALUE_ERROR, (year, _data))
                    return result
            year_data_dict[year] = _data

        await redis_conn.hset(app_id_key, "check_times", str(check_time_list))
        await redis_conn.hset(app_id_key, "important_days", str(important_day_list))
        for year in year_data_dict.keys():
            await redis_conn.hset(app_id_key, "year_"+year, year_data_dict[year])

        result_dict = dict()
        if check_times and len(check_time_list) > 0:
            result_dict["check_times"] = check_time_list
        if important_days and len(important_day_list) > 0:
            result_dict["important_days"] = important_day_list
        if len(year_data_dict.keys()) > 0:
            result_dict["year_data"] = str(year_data_dict)
        result = ReedResult.get(ErrorCode.SUCCESS, result_dict)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        if method == "POST":
            await request.app.state.redis.hdel(app_id_key)
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result



"""
config struct
{"app_id": "test1", "check_times": ["8:30", "17:30", "0:00"], "important_days": ["{'type': 'normal', 'key': '1-1', 'value': 'test festival hahaha'}", "{'type': 'lunar', 'key': '9-12', 'value': 'Ender\u9634\u5386\u751f\u65e5'}", "{'type': 'week', 'key': '10-2-2', 'value': '\u5341\u6708\u7684\u7b2c2\u4e2a\u5468\u4e8c'}"], "2022": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000", "2099": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000", "2023": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000"}
"""