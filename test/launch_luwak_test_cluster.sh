#!/bin/bash

#
#   Run the luwak search topology on a local machine for testing
#

(cd ../util && \
    ./stage_demo_mode.sh && \
    ./kafka_add_documents.sh
)
(cd ../src/luwak_search && \
    mvn clean && \
    mvn package && \
    ./run_luwak_topology.sh)
