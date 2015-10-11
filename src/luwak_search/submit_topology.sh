#!/bin/bash
export STRAW_CONFIG=`pwd`/../../config/config.properties
/usr/local/storm/bin/storm kill "prod-topology"
echo "USING CONFIG FILE: $STRAW_CONFIG"
sleep 30
/usr/local/storm/bin/storm jar target/storming-luwak-search-0.0.1.jar straw.storm.LuwakSearchTopology "prod-topology"

