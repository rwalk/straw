#!/usr/bin/python3
'''
Sample from the twitter API and post results to a file or to Kafka.

To use, set credientials as enviornment variables, e.g.

export TWITTER_ACCESS_TOKEN=...

or 

source myfile

where myfile exports the authorization variables 
'''

import twython, json, re, argparse, subprocess, os, sys, time
from socket import timeout
from kafka import SimpleProducer, KafkaClient

####################
#    Constants
####################
access_token = os.environ["TWITTER_ACCESS_TOKEN"]
access_token_secret = os.environ["TWITTER_SECRET_TOKEN"] 
consumer_key = os.environ["TWITTER_CONSUMER_TOKEN"]
consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]

class StrawStreamer(twython.TwythonStreamer):

    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, outfile):
        super(StrawStreamer, self).__init__(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.outfile=outfile

    def on_success(self, data):
        if 'text' in data:
            self.outfile.write((json.dumps(data)+u'\n').encode('utf-8'))

    def on_error(self, status_code, data):
        print(status_code)

class KafkaStrawStreamer(twython.TwythonStreamer):
    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, host, port):
        super(KafkaStrawStreamer, self).__init__(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

        # connect to Kafka
        print("Connecting to Kafka node {0}:{1}".format(host, port))
        kafka = KafkaClient("{0}:{1}".format(host, port))
        self.producer = BufferedSimpleProducer(kafka, 100)

    def on_success(self, data):
        # TODO: add message queue so we can pass messages in bulk
        if 'text' in data:
            msg = (json.dumps(data)+u'\n').encode('utf-8')
            self.producer.send_messages(args.topic, msg)

    def on_error(self, status_code, data):
        print(status_code)    

class BufferedSimpleProducer:
    def __init__(self, kafka, chunk_size):
        self.producer = SimpleProducer(kafka)
        self.queues = {}
        self.chunk_size = chunk_size

    def send_messages(self, topic, msg):
        if topic not in self.queues:
            self.queues[topic]=[]
        if len(self.queues[topic])<self.chunk_size:
            self.queues[topic].append(msg)
        else:
            self.producer.send_messages(topic, *(self.queues[topic]))
            print("Sent {0} documents to Kafka.".format(len(self.queues[topic])))
            self.queues[topic] = []

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Python twitter firehose sampler")
    parser.add_argument("-f","--file", help="Output will be appended to this file.")
    parser.add_argument("-k","--kafka", help="A kafka broker node")
    parser.add_argument("-t","--topic", help="A kafka topic")
    parser.add_argument("-p","--port", default=9092, help="A kafka port, default 9200")
    args = parser.parse_args()
    if args.file is None and args.kafka is None:
        raise RuntimeError("Need either an output file or a kafka host")
    if args.kafka is not None and args.topic is None:
        raise RuntimeError("Need a topic for Kafka")

    # connect to twitter API
    twitter = twython.Twython(consumer_key, consumer_secret)
    
    # write to file or to Kafka
    if args.file is not None:
        with open(args.file, "ab") as f:
            while True:
                try:
                    stream = StrawStreamer(consumer_key, consumer_secret, access_token, access_token_secret, f)
                    stream.statuses.sample(language="en")
                except timeout as e:
                    print("GOT SOCKET ERROR: {0}".format(e))
                    print("Retrying connection after 500 second wait...")
                    f.flush()
                    time.sleep(500)
    else:
        while True:
            try:
                stream = KafkaStrawStreamer(consumer_key, consumer_secret, access_token, access_token_secret, args.kafka, args.port)
                stream.statuses.sample(language="en")
            except timeout as e:
                print("GOT SOCKET ERROR: {0}".format(e))
                print("Retrying connection after 500 second wait...")
                f.flush()
                time.sleep(500)
