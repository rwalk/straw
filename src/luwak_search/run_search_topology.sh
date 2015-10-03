#!/bin/bash
export STRAW_CONFIG=`pwd`/config/config.properties
echo "USING CONFIG FILE: $STRAW_CONFIG"
mvn compile exec:java -Dstorm.topology=straw.storm.StreamingSearchTopology
