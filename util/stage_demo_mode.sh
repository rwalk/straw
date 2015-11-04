#!/bin/bash

# unpack local data
( cd ../data/ &&
gunzip tweets.big.sample.gz -f -k
)


# start kafka
(cd ../src/kafka_stream_eater/third_party/kafka-docker-master && docker-compose stop && docker-compose rm && docker-compose up -d --force-recreate)

# start elasticsearch
./docker_elasticsearch.sh

