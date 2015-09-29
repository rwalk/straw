import thread, redis
from kafka import SimpleProducer, KafkaClient
from flask import Flask
from query_subscriber import QuerySubscriber
from views import attach_views

class StrawAppBase:

    def __init__(self, config):
    
        app = Flask(__name__)
        
        # Add Redis query subscriber to app
        app.disp = []
        app.subscriber = QuerySubscriber("localhost", 6379, app.disp)

        # setup kafka producer in the app
        kafka = KafkaClient("{0}:{1}".format(config["zookeeper_host"], 9092))
        app.producer = SimpleProducer(kafka)

        # attach a redis connection pool
        app.pool = redis.ConnectionPool(host="localhost", port=6379)

        self.app = app

def get_straw_app(config):
    app = StrawAppBase(config).app
    attach_views(app)
    return app



