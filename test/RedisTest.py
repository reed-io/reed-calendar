import redis

redis_config = {
    "host": "service.persona.net.cn",
    "port": 6379,
    "password": "Shashiyuefu@2021",
    "db": 15
}

pool = redis.ConnectionPool(host=redis_config["host"], port=redis_config["port"], password=redis_config["password"],
                   db=redis_config["db"], decode_responses=True)

redis_conn = redis.Redis(connection_pool=pool)


print(redis_conn.keys())
print(redis_conn.get("test1"))
print(redis_conn.hkeys("calendar_test7"))


