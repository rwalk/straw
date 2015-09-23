#!/bin/bash
#
#   Simple elasticsearch docker container for testing purposes
#   NOTE: Data does NOT pesist here since we don't care to mount a volume

docker run --name elasticsearch -d -p 9200:9200 -p 9300:9300 elasticsearch:latest
echo "Waiting 30 seconds for elasticsearch to be available"
sleep 30
echo "adding a documents index..."
curl -XPUT localhost:9200/documents -d '{
    "mappings": {
        "document": {
            "properties": {
                "text": {
                    "type": "string"
                }
            }
        }
    }
}'
echo "done"


