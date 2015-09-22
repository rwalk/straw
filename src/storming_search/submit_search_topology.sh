#!/bin/bash
export STRAW_CONFIG=`pwd`/config/config.properties
echo "USING CONFIG FILE: $STRAW_CONFIG"
/usr/local/storm/bin/storm jar target/storming-search-0.0.1.jar straw.storm.StreamingSearchTopology "prod-topology"

