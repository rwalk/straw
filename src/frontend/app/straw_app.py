import thread, redis
from kafka import SimpleProducer, KafkaClient
from flask import Flask
from query_subscriber import QuerySubscriber
from views import attach_views
from datetime import datetime

def highlight(word):
    return("<span style=\"background-color: #FFFF00\">{0}</span>".format(word))

class StrawAppBase:

    def __init__(self, config):
    
        app = Flask(__name__)

        # attach a redis connection pool
        app.pool = redis.ConnectionPool(host="localhost", port=6379)

        def redis_message_handler(msg):
            redis_connection = redis.Redis(connection_pool=app.pool)

            # for benchmarking, add a time stamp to the message 
            if config['benchmark']:
                msg['data']=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f ') + msg['data']
            
            # word highlighting -- TODO: this would be better to do in the search engine!
            query_list = redis_connection.lrange("queries", 0, -1)
            words = []
            for q in query_list:
                words.extend(q.split(" "))
            words = list(set(words))
            for w in words:
                msg['data']=msg['data'].replace(w, highlight(w))

            # move the recieved messages into the redis "matches" table
            redis_connection.lpush('matches', msg['data'])
            
        # Add Redis query subscriber to app
        app.disp = []
        app.subscriber = QuerySubscriber("localhost", 6379, redis_message_handler)

        # setup kafka producer in the app
        kafka = KafkaClient("{0}:{1}".format(config["zookeeper_host"], 9092))
        app.producer = SimpleProducer(kafka)

        self.app = app

def get_straw_app(config):
    app = StrawAppBase(config).app
    attach_views(app)
    return app



