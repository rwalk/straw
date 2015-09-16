#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Simple tweet client calls to collect some example tweet data.
@author: ryan
"""
import tweepy, json, re, argparse, subprocess, os, sys

####################
#    Constants
####################
access_token = os.environ["TWITTER_ACCESS_TOKEN"]
access_token_secret = os.environ["TWITTER_SECRET_TOKEN"] 
consumer_key = os.environ["TWITTER_CONSUMER_TOKEN"]
consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]

#####################
#    Listener
#####################

class StdOutListener(tweepy.StreamListener):
    
    def __init__(self, outfile):
        super(StdOutListener, self).__init__()
        self.outfile=outfile 

    def on_status(self, status):
        #  data = rawjson.decode('utf-8')
        data = json.dumps(status._json)
        print(data)
        self.outfile.write(data+"\n")

    def on_error(self, status):
        print(status)
        outfile.close()
        return(False)

if __name__ == '__main__':

    # arg parsing
    parser = argparse.ArgumentParser(description="Python twitter feed listener")
    parser.add_argument("file", help="Output will be appended to this file.")
    parser.add_argument("-ns", "--nostream", dest="nostream", action='store_true', help="Print first 20 tweets in timeline and quit.")    
    args = parser.parse_args()
    
    # authenticate
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # file
    f = open(args.file, "a+")

    if args.nostream==False:
        # stream from user's timeline
        l = StdOutListener(f)
        stream = tweepy.Stream(auth=api.auth, listener=l)
        stream.userstream()        
    else:
        # fetch the top of the user's timeline
        data = api.home_timeline()
        for tl in data:
            rawjson = json.dumps(tl._json)
            f.write(rawjson+"\n")
            print(rawjson)
        f.close()
