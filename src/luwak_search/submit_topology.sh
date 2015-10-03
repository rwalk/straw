#!/bin/bash
export STRAW_CONFIG=`pwd`/../../config/config.properties
/usr/local/storm/bin/storm kill "prod-topology"
/usr/local/storm/bin/storm deactivate "prod-topology"
echo "USING CONFIG FILE: $STRAW_CONFIG"
/usr/local/storm/bin/storm jar target/storming-luwak-search-0.0.1.jar straw.storm.LuwakSearchTopology "prod-topology"

