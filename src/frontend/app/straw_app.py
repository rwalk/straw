import thread, redis
from kafka import SimpleProducer, KafkaClient
from flask import Flask, session
from flask.ext.session import Session
from query_subscriber import QuerySubscriber
from views import attach_views
from datetime import datetime

def highlight(word):
    return("<span style=\"background-color: #FFFF00\">{0}</span>".format(word))

class StrawAppBase:

    def __init__(self, config):
    
        app = Flask(__name__)
        app.secret_key = 'i love to search full text in real time'

        # attach a redis connection pool
        app.pool = redis.ConnectionPool(host="localhost", port=6379)

        # user -> channels mapping
        app.user_channels = {}

        # how to handle messages that enter the stream from redis pub sub
        def redis_message_handler(msg):
            redis_connection = redis.Redis(connection_pool=app.pool)
            # get channel and content of incoming message
            channel = msg['channel']
            data = msg['data']

            # word highlighting -- TODO: this would be better to do in the search engine!
            query = redis_connection.get(channel)
            words = list(set(query.split(" ")))
            for w in words:
                data=data.lower().replace(w.lower(), highlight(w.lower()))

            # find users subscribed to this channel
            if app.user_channels.get(channel) is not None:
                for user in app.user_channels.get(channel):
                    redis_connection.lpush(user, data)
            else:
                # no more users for this channel, unsubscribe from it
                redis_connection.unsubscribe(channel)            
            
        # Add Redis query subscriber to app
        app.disp = []
        app.subscriber = QuerySubscriber("localhost", 6379, redis_message_handler)

        # setup kafka producer in the app
        kafka = KafkaClient("{0}:{1}".format(config["zookeeper_host"], 9092))
        app.producer = SimpleProducer(kafka)

        # add the app
        self.app = app

    def clear_user(self, uid):
        redis_connection = redis.Redis(connection_pool=self.app.pool)
        print("Trying to clean for user {0}".format(uid))
        # find all the queries to which the user is subscribed
        # and remove them from the subscribers list for each query.
        for qid in redis_connection.lrange(uid+"-queries", 0, -1):
            self.app.user_channels[qid].remove(uid)
            print(qid)

        # remove the user-queries
        redis_connection.delete(uid+"-queries")

        # remove the stored results
        redis_connection.delete(uid)

def get_straw_app(config):
    base = StrawAppBase(config)
    app = base.app
    app.clear_user = base.clear_user
    attach_views(app)
    return app



