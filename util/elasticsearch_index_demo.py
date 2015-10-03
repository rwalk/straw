#!/usr/bin/python3
#   This script is a simple introduction to the python elasticsearch API. 
#
#   This script will populate an elasticsearch index from a file and then give a simple command line query interface.
#   Each line of the input file will be mapped into a JSON document of the form { "text": "my file line..." } and added
#   to the index. 
#
#   You can use Docker to spin up a local elasticsearch instance to play around with, e.g.
#   docker run --name elasticsearch -d -p 9200:9200 elasticsearch:latest
#
import argparse, elasticsearch, json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

if __name__=="__main__":

    # argument help
    parser = argparse.ArgumentParser(description='Add lines from a file to a simple text Elasticsearch index.')
    parser.add_argument('file', help='Name of file to parse, e.g. /usr/share/dict/american-english')
    parser.add_argument('host', help='Elasticsearch host.')
    parser.add_argument('-p','--port', default=9200, help='port, default is 9200')
    args = parser.parse_args()

    # index and document type constants
    INDEX_NAME = "documents"
    TYPE = "document"

    # get a client
    es = Elasticsearch(hosts=[{"host":args.host, "port":args.port}])

    # create an index, ignore if it exists already
    es.indices.create(index='documents', ignore=400)

    # add a single document
    es.create(index='documents', doc_type='document', body={ 'text': "hello message!"})

    # json-ize the lines in the file
    def make_documents(f):
        for l in f:
            doc = {
                    '_op_type': 'create',
                    '_index': INDEX_NAME,
                    '_type': TYPE,
                    '_source': {'text': l.strip() }
            }
            yield( doc )            
        
    # put documents in index in bulk
    with open(args.file, "r") as f:            
        bulk(es, make_documents(f))

    # count the matches
    count = es.count(index=INDEX_NAME, doc_type=TYPE, body={ "query": {"match_all" : { }}})

    # now we can do searches.
    print("Ok. I've got an index of {0} documents. Let's do some searches...".format(count['count']))
    while True:
        try:
            query = input("Enter a search: ")
            result = es.search(index=INDEX_NAME, doc_type=TYPE, body={"query": {"match": {"text": query.strip()}}})
            if result.get('hits') is not None and result['hits'].get('hits') is not None:
                print(result['hits']['hits'])
            else:
                print({})
        except(KeyboardInterrupt):
            break
