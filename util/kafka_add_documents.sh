#!/bin/bash

# add data to kafka
(cd ../kafka_stream_eater \
  && ./kafka_stream_producer.py ../../data/tweets.big.sample localhost documents \
)

