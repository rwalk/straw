#!/usr/bin/python3

import twython, json, re, argparse, subprocess, os, sys, time

####################
#    Constants
####################
access_token = os.environ["TWITTER_ACCESS_TOKEN"]
access_token_secret = os.environ["TWITTER_SECRET_TOKEN"] 
consumer_key = os.environ["TWITTER_CONSUMER_TOKEN"]
consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]


class StrawStreamer(twython.TwythonStreamer):

    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, outfile, outfile2):
        super(StrawStreamer, self).__init__(APP_KEY, APP_SECRET,OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.outfile=outfile

    def on_success(self, data):
        if 'text' in data:
            self.outfile.write((json.dumps(data)+u'\n').encode('utf-8'))
            print(data)

    def on_error(self, status_code, data):
        print(status_code)

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Python twitter firehose sampler")
    parser.add_argument("file", help="Output will be appended to this file.")
    args = parser.parse_args()

    twitter = twython.Twython(consumer_key, consumer_secret)
    with open(args.file, "ab") as f:
        with open(args.file+'.text', "ab") as f2:
            stream = StrawStreamer(consumer_key, consumer_secret, access_token, access_token_secret, f, f2)
            stream.statuses.sample(language="en")
        
