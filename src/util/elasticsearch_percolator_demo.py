#!/usr/bin/python3
#   This script is a simple introduction to Elasticsearch percolators
#
#
#   You can use Docker to spin up a local elasticsearch instance to play around with, e.g.
#   docker run --name elasticsearch -d -p 9200:9200 elasticsearch:latest
#
import argparse, elasticsearch, json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import time

def perco_parse(result):
    # take the first match
    if result.get('matches') is not None and len(result['matches'])>0:
        return([int(r['_id']) for r in result['matches']][0])

if __name__=="__main__":

    # argument help
    parser = argparse.ArgumentParser(description='Create and test Elasticsearch percolators.')
    parser.add_argument('file', help='File of tweets, one json doc per line.')
    parser.add_argument('host', help='Elasticsearch host.')
    parser.add_argument('-p','--port', default=9200, help='port, default is 9200')
    args = parser.parse_args()

    # index and document type constants
    INDEX_NAME = "documents"
    TYPE = "document"

    # get a client
    es = Elasticsearch(hosts=[{"host":args.host, "port":args.port}])

    # create an index, ignore if it exists already
    es.indices.delete(index='documents', ignore=400)
    es.indices.create(index='documents', ignore=400, body={
          "mappings": {
            "document": {
              "properties": {
                "message": {
                  "type": "string"
                }
              }
            }
          }
        }
    )

    ###########################
    # add some percolators
    ###########################
    query_table=[]
    queries = ['new york', 'facebook', 'cheese', 'mountain', 'zoology', 'artist', 'tech', 'big data']
    for q in queries:
        es.create(index='documents', doc_type='.percolator', body={'query': {'match': {'message': q}}}, id=len(query_table))
        query_table.append(q)

    # now we can do some stream searches.
    counter = 0
    with open(args.file, 'rb') as f:
        for line in f:
            counter+=1
            try:
                tweet=json.loads(line.decode('utf-8').strip())
                msg = tweet['text']
                perco_match = perco_parse(es.percolate(index='documents', doc_type='document', body={'doc':{'message':msg}}))
                if perco_match is not None:
                    print("{0}:{1}:{2}".format(counter, query_table[perco_match], msg))
            except(ValueError) as e:
                print("BAD VALUE")
                    

