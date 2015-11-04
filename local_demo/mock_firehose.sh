#!/bin/bash
# This script simulates the twitter firehose by repeatedly
# adding the collection of 100k tweets included with this repo into Kafka.
#
# data can be found in data/tweets.big.sample
#
(
cd ../util &&
while true ; do
    ./kafka_add_documents.sh
    echo "Sleeping 10 so I don't swamp your puny local cluster!"
    sleep 10
done
)
