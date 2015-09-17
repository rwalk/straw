#!/bin/bash
#
#   Simple elasticsearch docker container for testing purposes
#   NOTE: Data does NOT pesist here since we don't care to mount a volume

docker run --name elasticsearch -d -p 9200:9200 elasticsearch:latest || { echo 'failed to start elasticsearch docker' ; exit 1; }

echo "Sleeping a few seconds before we start putting data into our elasticsearch cluster"
sleep(10)
# add some text to elasticsearch
DICTIONARY=/usr/share/dict/american-english

for p in ($DICTIONARY)
do
    echo "${p}"
done

