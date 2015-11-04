#!/bin/bash

#
#   This script attempts to install necassary dependencies for straw running on Ubuntu 14.04
#
#   NOTE: You will need to install docker manually, using at least version 1.8.0.
#

# redis
sudo apt-get install redis-server

# docker compose
( 
curl -L https://github.com/docker/compose/releases/download/1.5.0/docker-compose-`uname -s`-`uname -m` > tmp &&
sudo mv tmp /usr/local/bin/docker-compose &&
sudo chmod +x /usr/local/bin/docker-compose
)

# python2 packages -- flask only recommended for python2
sudo pip install redis flask flask-session kafka-python

# python3 packages
sudo pip3 install kafka-python
