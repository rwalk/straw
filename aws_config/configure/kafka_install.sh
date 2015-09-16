#!/bin/bash

# install java and zookeeper
apt-get update
apt-get install -y default-jre
apt-get install -y zookeeperd

# install kafka
mkdir -p ~/Downloads
wget "http://mirror.cc.columbia.edu/pub/software/apache/kafka/0.8.2.1/kafka_2.11-0.8.2.1.tgz" -P ~/Downloads
tar zxvf ~/Downloads/kafka_2.11-0.8.2.1.tgz -C /usr/local
mv /usr/local/kafka_2.11-0.8.2.1 /usr/local/kafka




