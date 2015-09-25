#!/usr/bin/python
#
#   Consume matches from subscribed queries
#
import redis
from time import sleep

def message_handler(data, message):
    data.append((message['channel'], message['data']))
 
class QuerySubscriber:

    def __init__(self, host, port, data_queue):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.StrictRedis(connection_pool=pool)
        self.connection = r.pubsub(ignore_subscribe_messages=True)
        self.queries = []
        self._thread = None
        self.handler = lambda x: message_handler(data_queue, x)     

    def add_query(self, query):
        # add query to list
        self.queries.append(query)

        # stop the existing thread and start new one with the full set of queries
        self._update()

    def start(self):
        queries = dict((k,v) for (k,v) in [(k,self.handler) for k in self.queries]) 
        self.connection.subscribe(**queries)
        self._thread = self.connection.run_in_thread(sleep_time=0.001)

    def _update(self):
        # WARNING: We might drop some messages here
        if self._thread is not None:
            self._thread.stop()
        self.start()
               
if __name__=="__main__":
    mydata = []
    subscriber = QuerySubscriber("localhost", 6379, message_handler, mydata)
    query = None
    while True:
        if query is None:
            query = raw_input("Please enter the topic you'd like to follow: ")
            print
            print mydata
        else:
            subscriber.add_query(query)
            query = None
