# -*- coding: utf-8 -*-

from utils.EnderUtil import StringUtil
from utils.EnderUtil import TimeUtil
from define.ReedResult import ReedResult
from define.EnderDay import EnderDay
from define.ReedCalendarErrorCode import ReedCalendarErrorCode as ErrorCode
from fastapi import APIRouter, Request, Form
from utils.DateTimeUtil import DateTimeUtil
from utils.SolarUtil import SolarUtil
import datetime
from define.BaseConst import ReedConst

import json
import re
import logging

private = APIRouter()

time_pattern = re.compile("((([01]\\d)|(2[0-3]))|(\d)):[0-5]\\d(:[0-5]\\d)?")


@private.get('/{app_id}/today', tags=["获取当天信息"])
async def today(app_id, request: Request):
    logging.debug(f"request param: app_id={app_id}")
    redis_conn = request.app.state.redis
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        key = __get_app_id_key(app_id)
        exists = await redis_conn.exists(key)
        if not exists:
            logging.warning("can not find " + key + " in redis!")
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        td = EnderDay()
        _result = td.to_dict()
        important_days = await redis_conn.hget(key, ReedConst.KEY_IMPORTANT_DAYS.value)
        logging.debug("redis hget(important_days)=" + important_days)
        print("redis", key, ReedConst.KEY_IMPORTANT_DAYS.value, important_days)
        important_days = json.loads(json.dumps(eval(important_days)))
        private_important_days = td._private_important_days(important_days)
        logging.debug("after handle private important_days=" + str(private_important_days))
        print("private_important_days", private_important_days)
        _result[ReedConst.KEY_IMPORTANT_DAYS.value] = private_important_days
        # _result[ReedConst.KEY_FESTIVALS.value] = _result[ReedConst.KEY_FESTIVALS.value] + private_important_days
        private_calendar_year_key = "year_" + str(td.get_datetime().year)
        hash_exists = await redis_conn.hexists(key, private_calendar_year_key)
        if hash_exists:
            private_calendar_year_data = await redis_conn.hget(key, private_calendar_year_key)
            print("private_calendar_year_data", private_calendar_year_data)
            _result[ReedConst.KEY_IS_WORK_DAY.value] = td._private_is_work_day(private_calendar_year_data)
        result = ReedResult.get(ErrorCode.SUCCESS, _result)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@private.get("/{app_id}/configuration", tags=["获取配置信息"])
async def get_configuration(app_id, request: Request):
    logging.debug(f"request param: app_id={app_id}")
    redis_conn = request.app.state.redis
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        key = __get_app_id_key(app_id)
        exists = await redis_conn.exists(key)
        if not exists:
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        result = dict()
        result["app_id"] = app_id
        check_times = await redis_conn.hget(key, "check_times")
        check_times = json.loads(json.dumps(check_times))
        result["check_times"] = eval(check_times)
        important_days = await redis_conn.hget(key, ReedConst.KEY_IMPORTANT_DAYS.value)
        important_days = json.loads(json.dumps(important_days))
        result[ReedConst.KEY_IMPORTANT_DAYS.value] = eval(important_days)
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
    logging.debug(f"request param: app_id={app_id},date={date}")
    redis_conn = request.app.state.redis
    try:
        if StringUtil.isEmpty(app_id):
            logging.warning("path args: app_id is empty!")
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
            return result
        if not TimeUtil.is_validate_date(date):
            logging.warning("invalidate date format")
            result = ReedResult.get(ErrorCode.DATE_INVALIDATE, date)
            return result

        key = __get_app_id_key(app_id)
        exists = await redis_conn.exists(key)
        if not exists:
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        d = EnderDay(TimeUtil.get_date(date))
        _result = d.to_dict()
        important_days = await redis_conn.hget(key, ReedConst.KEY_IMPORTANT_DAYS.value)
        print("redis", key, ReedConst.KEY_IMPORTANT_DAYS.value, important_days)
        important_days = json.loads(json.dumps(eval(important_days)))
        private_important_days = d._private_important_days(important_days)
        print("private_important_days", private_important_days)
        _result[ReedConst.KEY_IMPORTANT_DAYS.value] = private_important_days
        # _result[ReedConst.KEY_FESTIVALS.value] = _result[ReedConst.KEY_FESTIVALS.value] + private_important_days
        private_calendar_year_key = "year_" + str(d.get_datetime().year)
        hexists = await redis_conn.hexists(key, private_calendar_year_key)
        if hexists:
            private_calendar_year_data = await redis_conn.hget(key, private_calendar_year_key)
            print("private_calendar_year_data", private_calendar_year_data)
            _result[ReedConst.KEY_IS_WORK_DAY.value] = d._private_is_work_day(private_calendar_year_data)
        result = ReedResult.get(ErrorCode.SUCCESS, _result)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@private.api_route("/{app_id}/configuration", methods=["PUT", "POST"], tags=["创建或修改配置信息"])
async def post_put_configuration(app_id, request: Request, check_times=Form(None),
                                 important_days=Form(None)):
    logging.debug(f"request param: app_id={app_id}")
    logging.debug(f"request param: check_times = {check_times}")
    logging.debug(f"request param: important_days = {important_days}")
    redis_conn = request.app.state.redis
    method = request.method
    logging.debug(method)
    app_id_key = __get_app_id_key(app_id)
    try:
        params = await request.form()
        logging.debug("params=" + str(params))
        year_data = list(filter(lambda year: len(year) == 4 and 1900 < eval(year) < 3000, params))
        print(app_id, check_times, important_days, year_data)
        if StringUtil.isEmpty(app_id):
            result = ReedResult.get(ErrorCode.APPID_NOT_FOUND, app_id)
            return result
        if (check_times is None or len(check_times) == 0) and (important_days is None or len(important_days) == 0) \
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
            if type(important_days) != list:
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
                # await redis_conn.hset(app_id_key, ReedConst.KEY_IMPORTANT_DAYS.value, str(important_day_list))

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
        await redis_conn.hset(app_id_key, ReedConst.KEY_IMPORTANT_DAYS.value, str(important_day_list))
        for year in year_data_dict.keys():
            await redis_conn.hset(app_id_key, "year_" + year, year_data_dict[year])

        result_dict = dict()
        if check_times and len(check_time_list) > 0:
            result_dict["check_times"] = check_time_list
        if important_days and len(important_day_list) > 0:
            result_dict[ReedConst.KEY_IMPORTANT_DAYS.value] = important_day_list
        if len(year_data_dict.keys()) > 0:
            result_dict["year_data"] = year_data_dict
        result = ReedResult.get(ErrorCode.SUCCESS, result_dict)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        if method == "POST":
            await request.app.state.redis.hdel(app_id_key)
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


@private.put("/{app_id}/{date}", tags=["设置指定日期信息"])
async def put_date_configuration(request: Request, app_id: str, date: str, is_work=Form(None),
                                 date_des_list=Form(None)):
    logging.debug(f"request param: app_id={app_id}, date={date}")
    redis_conn = request.app.state.redis
    if StringUtil.isEmpty(app_id):
        logging.error("path args app_id is empty!")
        result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
        return result
    if not TimeUtil.is_validate_date(date):
        logging.error("path args date is invalidate")
        result = ReedResult.get(ErrorCode.DATE_INVALIDATE)
        return result
    if is_work:
        if str(is_work) != "0" and str(is_work) != "1":  # 0=工作, 1=休息
            logging.error("form args is_work is invalidate")
            result = ReedResult.get(ErrorCode.IS_WORK_INVALIDATE, is_work)
            return result

    if date_des_list:
        date_des_list = eval(date_des_list)
        if type(date_des_list) is not list:
            logging.error("form args date_des_list is invalidate")
            result = ReedResult.get(ErrorCode.DATE_DES_LIST_INVALIDATE, date_des_list)
            return result
        for des in date_des_list:
            if type(des) is not str or StringUtil.isEmpty(des):
                logging.error("form args date_des_list contains bad item")
                result = ReedResult.get(ErrorCode.DATE_DES_LIST_ITEM_INVALIDATE, [date_des_list, des])
                return result

    app_id_key = __get_app_id_key(app_id)
    d = TimeUtil.get_date(date)
    year_key = "year_" + str(d.year)
    app_id_exists = await redis_conn.exists(app_id_key)
    modified_dict = {}
    if not app_id_exists:
        logging.error(f"{app_id} never configured yet")
        result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED, app_id)
        return result
    if is_work:
        year_config_exists = await redis_conn.hexists(app_id_key, year_key)
        if not year_config_exists:
            logging.error(f"{app_id} config can not find {year_key}")
            result = ReedResult.get(ErrorCode.YEAR_CONFIG_NOT_FOUND, d.year)
            return result
        year_work_days = await redis_conn.hget(app_id_key, year_key)
        logging.debug(f"before modify:{year_work_days}")
        date_idx = TimeUtil.get_days_index(d)
        year_work_days_list = list(year_work_days)
        year_work_days_list[date_idx] = is_work
        logging.debug(f"set {date_idx} of {year_work_days_list} to {is_work}")
        year_work_days = "".join(year_work_days_list)
        logging.debug(f"after modify:{year_work_days}")
        await redis_conn.hset(app_id_key, year_key, year_work_days)
        modified_dict[str(d.year)] = year_work_days

    app_id_important_days = await redis_conn.hget(app_id_key, ReedConst.KEY_IMPORTANT_DAYS.value)
    logging.debug(type(app_id_important_days))
    logging.debug(str(app_id_important_days))
    # important_day = filter(lambda item: item["type"] == "normal" and item["key"] == str(d.month)+"-"+str(d.day), app_id_important_days)
    contains_flag = False
    app_id_important_days = eval(app_id_important_days)
    for important_day in app_id_important_days:
        # important_day = eval(important_day)
        if important_day["type"] == "normal" and important_day["key"] == str(d.month) + "-" + str(d.day):
            if date_des_list:
                important_day["value"] = ",".join(date_des_list)
            else:
                """删除定义的normal类型纪念日"""
                app_id_important_days.remove(important_day)
            contains_flag = True
            break
    if date_des_list and not contains_flag:
        important_day = {
            "type": "normal",
            "key": str(d.month) + "-" + str(d.day),
            "value": ",".join(date_des_list)
        }
        app_id_important_days.append(important_day)
    await redis_conn.hset(app_id_key, ReedConst.KEY_IMPORTANT_DAYS.value, str(app_id_important_days))
    modified_dict[ReedConst.KEY_IMPORTANT_DAYS.value] = app_id_important_days

    result = ReedResult.get(ErrorCode.SUCCESS, modified_dict)
    return result


@private.get("/{app_id}/month/{year}/{month}")
async def month_calendar(app_id, year: int, month: int, request: Request):
    logging.debug(f"request param: app_id={app_id},year={year},month={month}")
    if StringUtil.isEmpty(app_id):
        logging.warning("path args: app_id is empty!")
        result = ReedResult.get(ErrorCode.APPID_NOT_FOUND)
        return result
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
    try:
        redis_conn = request.app.state.redis
        key = __get_app_id_key(app_id)
        exists = await redis_conn.exists(key)
        if not exists:
            logging.warning("can not find " + key + " in redis!")
            result = ReedResult.get(ErrorCode.APPID_NOT_CONFIGURED)
            return result
        important_days = await redis_conn.hget(key, ReedConst.KEY_IMPORTANT_DAYS.value)
        logging.debug("redis hget(important_days)=" + important_days)
        print("redis", key, ReedConst.KEY_IMPORTANT_DAYS.value, important_days)
        important_days = json.loads(json.dumps(eval(important_days)))

        month_first_date = DateTimeUtil.fromYmd(year, month, 1)
        first_date = SolarUtil.getWeekFirstDay(month_first_date)

        current_calendar_year_key = "year_" + str(year)
        current_calendar_year_data = str()
        other_calendar_year_key = str()
        other_calendar_year_data = str()
        if first_date.year == year:
            other_calendar_year_key = "year_" + str(year + 1)
        else:
            other_calendar_year_key = "year_" + str(year - 1)
        hash_exists = await redis_conn.hexists(key, current_calendar_year_key)
        if hash_exists:
            current_calendar_year_data = await redis_conn.hget(key, current_calendar_year_key)
        hash_exists = await redis_conn.hexists(key, other_calendar_year_key)
        if hash_exists:
            other_calendar_year_data = await redis_conn.hget(key, other_calendar_year_key)

        datas = list()
        for i in range(0, 42):
            n = datetime.timedelta(days=i)
            date = first_date + n
            day_info = EnderDay(date)
            private_important_days = day_info._private_important_days(important_days)
            # logging.debug("after handle private important_days=" + str(private_important_days))
            data_info = day_info.to_dict()
            data_info[ReedConst.KEY_IMPORTANT_DAYS.value] = private_important_days
            # data_info[ReedConst.KEY_FESTIVALS.value] = _result[ReedConst.KEY_FESTIVALS.value] + private_important_days
            if day_info.get_year() == year:
                data_info[ReedConst.KEY_IS_WORK_DAY.value] = day_info._private_is_work_day(current_calendar_year_data)
            else:
                data_info[ReedConst.KEY_IS_WORK_DAY.value] = day_info._private_is_work_day(other_calendar_year_data)
            datas.append(data_info)
        result = ReedResult.get(ErrorCode.SUCCESS, data=datas)
        return result
    except Exception as e:
        logging.error(e.with_traceback())
        result = ReedResult.get(ErrorCode.UNKNOWN_ERROR, e.__dict__)
        return result


def __get_app_id_key(app_id: str):
    # return "calendar_" + app_id
    return ReedConst.KEY_REDIS_APP_PREFIX.value + app_id


"""
config struct
{"app_id": "test1", "check_times": ["8:30", "17:30", "0:00"], "important_days": ["{'type': 'normal', 'key': '1-1', 'value': 'test festival hahaha'}", "{'type': 'lunar', 'key': '9-12', 'value': 'Ender\u9634\u5386\u751f\u65e5'}", "{'type': 'week', 'key': '10-2-2', 'value': '\u5341\u6708\u7684\u7b2c2\u4e2a\u5468\u4e8c'}"], "2022": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000", "2099": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000", "2023": "01100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000110000011000001100000"}
"""
