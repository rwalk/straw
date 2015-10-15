#!/bin/bash

### Agree to stupid oracle license nonsense
### See http://stackoverflow.com/questions/19275856/auto-yes-to-the-license-agreement-on-sudo-apt-get-y-install-oracle-java7-instal
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections 

### Install Java 8
apt-get update
apt-get install -y python-software-properties
add-apt-repository -y ppa:webupd8team/java
apt-get update
apt-get install -y oracle-java8-installer

### 
apt-get install -y scala

# Install sbt
wget https://dl.bintray.com/sbt/debian/sbt-0.13.7.deb -P ~/Downloads
dpkg -i ~/Downloads/sbt-0.13.7.deb
apt-get install sbt

# Install Spark
wget http://apache.mirrors.tds.net/spark/spark-1.4.1/spark-1.4.1-bin-hadoop2.4.tgz -P ~/Downloads
tar zxvf ~/Downloads/spark-1.4.1-bin-hadoop2.4.tgz -C /usr/local
sudo mv /usr/local/spark-1.4.1-bin-hadoop2.4 /usr/local/spark
sudo chown -R ubuntu /usr/local/spark


