#!/usr/bin/env python
from app.straw_app import get_straw_app
import redis
if __name__=="__main__":

    # a dumb little config reader
    with open("../storming_search/config/config.properties", "r") as f:
        lines = f.readlines()

    config={}
    for line in lines:
        if line.find("=")!=-1:
            ls = line.split("=")
            config[ls[0]]=ls[1]

    # get the app and clear the redis db
    app = get_straw_app(config)
    redis_connection = redis.Redis(connection_pool=app.pool)
    redis_connection.flushall()
    app.run(host='0.0.0.0', debug = True)

