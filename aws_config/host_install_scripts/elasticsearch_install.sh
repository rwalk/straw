#!/bin/bash

#
#   Config/install elasticsearch 1.7 on Ubuntu 14.04   
#
#   Forked from https://gist.github.com/ricardo-rossi/8265589463915837429d
#   and modified by rwalker.
#
#

### Agree to stupid oracle license nonsense
### See http://stackoverflow.com/questions/19275856/auto-yes-to-the-license-agreement-on-sudo-apt-get-y-install-oracle-java7-instal
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections 

### Install Java 8
apt-get install -y python-software-properties
add-apt-repository -y ppa:webupd8team/java
apt-get update
apt-get install -y oracle-java8-installer

### Download and install the Public Signing Key
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -

### Setup Repository
echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" | tee -a /etc/apt/sources.list.d/elk.list

### Install Elasticsearch
#apt-get purge elasticsearch -y
apt-get update && sudo apt-get install elasticsearch -y

### node discovery plugin for AWS
/usr/share/elasticsearch/bin/plugin install elasticsearch/elasticsearch-cloud-aws/2.5.0

### start elasticsearch:
# service elasticsearch start
### To test:
# curl <IP>:9200

