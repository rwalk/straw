#!/bin/bash

# add data to kafka
(cd ../src/kafka_stream_eater \
  && ./kafka_stream_producer.py ../../data/tweets.big.sample localhost documents --delay 2 \
)

