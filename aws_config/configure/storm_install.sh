#!/bin/bash

# install java and zookeeper
apt-get update
apt-get install -y default-jre
apt-get install -y zookeeperd
apt-get install -y supervisor

# install storm
wget "http://mirrors.gigenet.com/apache/storm/apache-storm-0.9.5/apache-storm-0.9.5.tar.gz" -P ~/Downloads
tar zxvf ~/Downloads/apache-storm*.gz -C /usr/local
mv /usr/local/apache-storm* /usr/local/storm

# inject some new config
echo "export STORM_HOME=/usr/local/storm" | tee -a  /home/ubuntu/.profile /home/ubuntu/.bashrc
echo "export PATH=$PATH:$STORM_HOME/bin" | tee -a /home/ubuntu/.profile /home/ubuntu/.bashrc


# create space for local state
mkdir /usr/local/storm/local_state
chown ubuntu /usr/local/storm/local_state



