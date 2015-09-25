#!/usr/bin/env python
from time import sleep
from app import app
from app.query_subscriber import QuerySubscriber
import thread
from kafka import SimpleProducer, KafkaClient




if __name__=="__main__":

    with open("../storming_search/config/config.properties", "r") as f:
        lines = f.readlines()

    config={}
    for line in lines:
        if line.find("=")!=-1:
            ls = line.split("=")
            config[ls[0]]=ls[1]

    # Move messages to display box in background
    
    # setup the subscriber system
    app.disp = []
    app.subscriber = QuerySubscriber("localhost", 6379, app.disp)

    # setup kafka producer
    kafka = KafkaClient("{0}:{1}".format(config["zookeeper_host"], 9092))
    app.producer = SimpleProducer(kafka)

    # run the app
    app.run(host='0.0.0.0', debug = True)

