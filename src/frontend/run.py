#!/usr/bin/env python
from time import sleep
from app import app
from app.query_subscriber import QuerySubscriber
import thread
from kafka import SimpleProducer, KafkaClient

if __name__=="__main__":

    # Move messages to display box in background

    # setup the subscriber system
    app.disp = []
    app.subscriber = QuerySubscriber("localhost", 6379, app.disp)

    # setup kafka producer
    kafka = KafkaClient("{0}:{1}".format("localhost", 9092))
    app.producer = SimpleProducer(kafka)

    # run the app
    app.run(host='0.0.0.0', debug = True)

