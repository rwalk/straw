#!/bin/bash
##########################################################
#   Flask Webserver setup
##########################################################

# python3 discouraged: http://flask.pocoo.org/docs/0.10/python3/
apt-get -y update
apt-get install -y python-pip python-dev build-essential
pip install flask

# directories for content
cd /home/ubuntu/
mkdir app
mkdir app/static
mkdir app/templates
mkdir tmp

# initialize
touch app/__init__.py
echo "from flask import Flask" >> app/__init__.py
echo "app = Flask(__name__)" >> app/__init__.py
echo "from app import views" >> app/__init__.py

# change owner to ubuntu user
chown -R ubuntu:ubuntu app
chown -R ubuntu:ubuntu tmp
