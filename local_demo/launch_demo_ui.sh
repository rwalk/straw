#!/bin/bash
#
#   Launch the local UI for running in DEMO mode
#   Visit http://localhost:5000 in a browser to see the results
#
#
(
    cd ../src/frontend &&
    ./run.py -p 5000 --debug
)
