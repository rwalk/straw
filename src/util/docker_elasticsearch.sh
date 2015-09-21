#!/bin/bash
#
#   Simple elasticsearch docker container for testing purposes
#   NOTE: Data does NOT pesist here since we don't care to mount a volume

docker run --name elasticsearch -d -p 9200:9200 -p 9300:9300 elasticsearch:latest


