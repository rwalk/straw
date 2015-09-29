#!/usr/bin/env python
from app.straw_app import get_straw_app

if __name__=="__main__":

    # a dumb little config reader
    with open("../storming_search/config/config.properties", "r") as f:
        lines = f.readlines()

    config={}
    for line in lines:
        if line.find("=")!=-1:
            ls = line.split("=")
            config[ls[0]]=ls[1]

    # run the app
 
    app = get_straw_app(config)
    app.run(host='0.0.0.0', debug = True)

