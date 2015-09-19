#!/bin/bash
##########################################################
#   Flask Webserver setup
##########################################################

# python3 discouraged: http://flask.pocoo.org/docs/0.10/python3/
sudo apt-get -y update
sudo apt-get install -y python-pip python-dev build-essential
sudo pip install flask

