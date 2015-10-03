#!/usr/bin/python
#
#   Simple example of redis pubsub management in Python.
#
import redis
from time import sleep

if __name__=="__main__":

    # open the connection
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub(ignore_subscribe_messages=True)

    # what to do with the messages?
    def message_handler(message):
        print('MSG:', message['data'])
    
    query = raw_input("Please enter the topic you'd like to follow: ")

    # subscribe to first topic in background thread
    queries = {query: message_handler}
    p.subscribe(**queries)
    thread = p.run_in_thread(sleep_time=0.001)
    query = None

    # listen for a new query, if we get one then stop the running thread
    # and start a new one with an updated set of subscriptions
    # warning, we could get duplicates in the time it takes to bring up the new thread
    while True:
        if query is None:
            query = input("Please enter the topic you'd like to follow: ")
        else:
            # the old thread is now out of date (since it doesn't have all our subscriptions)
            thread_stale = thread
            
            # start a new thread with the full set of subscriptions
            queries[query] = message_handler
            query = None
            p.subscribe(**queries)
            thread = p.run_in_thread(sleep_time=0.001)

            # now kill off the old thread.
            thread_stale.stop()    
