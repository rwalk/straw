#!/usr/bin/env python
from app.straw_app import get_straw_app
import redis
import argparse

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Launch straw webserver frontend")
    parser.add_argument("-p", "--port", default=5000, help="port, default 5000")
    parser.add_argument("--debug", help="Use flask debug mode, default False.", action="store_true")
    args = parser.parse_args()

    with open("../../config/config.properties", "r") as f:
        lines = f.readlines()

    config={}
    for line in lines:
        if line.find("=")!=-1:
            ls = line.split("=")
            config[ls[0]]=ls[1]
    config["debug"]=args.debug
    
    # get the app and clear the redis db
    app = get_straw_app(config)
    redis_connection = redis.Redis(connection_pool=app.pool)
    redis_connection.flushall()
    app.run(host='0.0.0.0', port=int(args.port), debug = args.debug)

