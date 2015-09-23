#!/bin/bash

# start kafka
(cd ../kafka_stream_eater/third_party/kafka-docker-master && docker-compose stop && docker-compose rm && docker-compose up -d --force-recreate)

# start elasticsearch
./docker_elasticsearch.sh

# add data to kafka
(cd ../kafka_stream_eater \
  && ./kafka_stream_producer.py ../../data/tweets.small localhost documents \
  && ./kafka_stream_producer.py ../../data/queries.small localhost queries
)

