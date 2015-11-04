#!/bin/bash

#
#   This script attempts to install necassary dependencies for straw running on Ubuntu 14.04
#
#   NOTE: You will need to install docker manually, using at least version 1.8.0.
#
#   DOCKER INSTALL INSTRUCTIONS from http://docs.docker.com/engine/installation/ubuntulinux/
#	
#   sudo apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
#   sudo vi /etc/apt/sources.list.d/docker.list
#   Add the line "deb https://apt.dockerproject.org/repo ubuntu-trusty main" and save
#   sudo apt-get install docker-engine
#   sudo service docker start
#   sudo usermod -aG docker $USER
#   Log out and log in again


# redis
sudo apt-get update
sudo apt-get install redis-server python3-pip python-pip maven openjdk-7-jdk

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
