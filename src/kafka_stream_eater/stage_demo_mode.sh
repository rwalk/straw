#!/bin/bash
(cd third_party/kafka-docker-master/ && docker-compose stop && docker-compose rm && docker-compose up -d --force-recreate)
sleep 15
./kafka_stream_producer.py ../../data/tweets.sample localhost documents
./kafka_stream_producer.py ../../data/queries.small localhost queries

