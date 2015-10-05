#!/bin/bash

if [ $# -ne 1 ]; then
    echo "USAGE: $0 [number of queries]"
else
    echo "Posting $1 queries to Kafka"

    # take top n from bigrams file
    head -n $1 ../data/queries.bigrams > queries.tmp

    # add data to kafka
    ../src/kafka_stream_eater/kafka_stream_producer.py queries.tmp localhost queries

    rm queries.tmp
fi
