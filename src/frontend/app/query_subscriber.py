#!/usr/bin/python
#
#   Consume matches from subscribed queries
#
import redis
from time import sleep

def message_handler(data, message):
    data.append((message['channel'], message['data']))
 
class QuerySubscriber:

    def __init__(self, host, port, msg_handler):
        ''' Query subscriber takes an arbitrary msg_handler which is a function
            of a single variable message.'''
        pool = redis.ConnectionPool(host='localhost', port=6379)
        r = redis.Redis(connection_pool=pool)
        self.connection = r.pubsub(ignore_subscribe_messages=True)
        self.queries = []
        self._thread = None
        self.handler = msg_handler   

    def add_query(self, query):
        # add query to list
        self.queries.append(query)

        # stop the existing thread and start new one with the full set of queries
        self._update()

    def start(self):
        queries = dict((k,v) for (k,v) in [(k,self.handler) for k in self.queries])
        if len(queries)>0: 
            self.connection.subscribe(**queries)
            self._thread = self.connection.run_in_thread(sleep_time=0.001)
        else:
            self._thread = None
	
    def _update(self):
        # WARNING: We might drop some messages here
        if self._thread is not None:
            self._thread.stop()
            self._thread=None
        self.start()

    def close(self):
        try:
            self._thread.stop()
        except:
            pass

if __name__=="__main__":
    mydata = []
    subscriber = QuerySubscriber("localhost", 6379, lambda x: message_handler(mydata, x)  )
    query = None
    while True:
        if query is None:
            query = raw_input("Please enter the topic you'd like to follow: ")
        else:
            subscriber.add_query(query)
            query = None
            print mydata
