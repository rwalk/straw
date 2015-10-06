#!/bin/bash

#
#   Run the percolator search topology on a local machine for testing
#

(cd ../util && \
    ./stage_demo_mode.sh && \
    ./kafka_add_documents.sh
)
(cd ../src/storming_search && \
    mvn clean && \
    mvn package && \
    ./run_search_topology.sh)
