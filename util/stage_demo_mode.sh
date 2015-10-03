#!/bin/bash

# start kafka
(cd ../src/kafka_stream_eater/third_party/kafka-docker-master && docker-compose stop && docker-compose rm && docker-compose up -d --force-recreate)

# start elasticsearch
./docker_elasticsearch.sh

echo "Sleep additional 30 seconds to give Kafka cluster time to configure itself"
sleep 30
# add data to kafka
(cd ../src/kafka_stream_eater \
  && ./kafka_stream_producer.py ../../data/tweets.small localhost documents \
  && ./kafka_stream_producer.py ../../data/queries.small localhost queries
)

