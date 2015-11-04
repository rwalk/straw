#!/bin/bash
#
#   This script helps run the demo mode with the Luwak search topology on a local cluster
#   The below commands stage system resources in docker containers and then builds   
#   the main Luwak topology storm cluster.  
#
#   You'll want to launch the WEB UI in a seperate terminal/process. 
#   For this:
#       cd src/frontend
#       ./run.py.  
#   See run.py -h for help.
#
#   To simulate the twitter firehose, run ./mock_firehose.sh
#

# startup local resources in docker containers
( cd ../util &&
./stage_demo_mode.sh
)

# build libraries
(cd ../src/luwak_search &&
mvn clean &&
mvn package
)

# launch local storm cluster with luwak topology
(cd ../src/luwak_search &&
./run_luwak_topology.sh
)


