# straw
A platform for real-time streaming search

The goal of this project is to provide a clean, scalable architecture for real-time search on streaming data.  Additionally, the project contains utilities to provide some very simple throughput benchmarking of Elasticsearch Percolators vs Lucence-Luwak.  Preliminary benchmarks may be found in:

http://straw.ryanwalker.us/about

Comments and critiques about these benchmarks are greatly appreciated!

This project was inspired by the following excellent blog posts on streaming search: 
- http://www.confluent.io/blog/real-time-full-text-search-with-luwak-and-samza/
- http://www.flax.co.uk/blog/2015/07/27/a-performance-comparison-of-streamed-search-implementations/

I completed this project as a Fellow in the 2015C Inisght Data Engineering Silicon Valley program.

## What's included:
- Automated AWS cluster deployment utilities using boto3
- Java based Storm implementation:
  - KafkaSpout for query and document spouts
  - Two flavors of streaming search bolts:
    - [Elasticsearch-Percolators](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-percolate.html)
    - Pure Lucene with [Luwak](https://github.com/flaxsearch/luwak)
  - Storm toplogy for streaming search and configuration management
- Scripts to populate document streams, including twitter API sampling utilities
- Simple Python flask web UI
- Testing and other utilities, including Docker components so that the entire topology can run on a local machine

## Architechture
The core of the platform is an Apache Storm cluster which parallelizes the work of real-time streaming search.  Internally, the Storm cluster consumes messages from a Kafka cluster and these messages are distributed to bolts which each contain a Lucene-Luwak index.  The project contains a demo flask UI which handles subscriptions with a Redis PUBSUB system.

More about the architecture can be found at:
http://straw.ryanwalker.us/about

## Getting started
### Running locally
1. install docker-compose and redis-server
2. run src/util/stage_demo_mode.sh  This will create dockers for Kafka with Zookeeper and Elasticsearch and will populate these services with some example data.  [BUG: You may have to run this script twice!]
3. cd src/storming_search OR src/luwak_search
4. run mvn package
5. ./run_search_topology.sh [BUG: You need to push lots of documents to Kafka or you'll get an error]
6. In a seperate terminal, activate the frontend by calling ./run.py from src/frontend

### Deploy to AWS
Prerequisites: You need
1. The aws cli
2. Python boto3
3. Set your default configurations by calling "aws configure"
4. Modify the settings in `straw_service_config.sh` to your own AWS account information.

Steps:
1. `cd src/aws_config`
2. `/create_clusters.py --help` to get instructions about this AWS creation script and follow instructions.
3. Once all resources are created, `cd configure`. This directory contains scripts to configure each of the individual services; you'll need to run each of these to configure the resource, e.g. `./configure_elasticsearch`.
4. Once resources are created, run
```
./discover.py
```
to see the list of services and their IPs.
5. To submit or run topologies, you need to install storm on your machine (or, even better, on a dedicted machine within the subnet of the Storm cluster).  Install storm as follows:
```
sudo apt-get update
sudo apt-get install openjdk-7-jdk
wget http://mirrors.gigenet.com/apache/storm/apache-storm-0.9.5/apache-storm-0.9.5.tar.gz -P ~/Downloads
sudo tar zxvf ~/Downloads/apache-storm*.gz -C /usr/local
sudo mv /usr/local/apache-storm* /usr/local/storm
```
Then `vi /usr/local/storm/config/storm.yml` and add the line
```nimbus.host: 10.X.X.X```
using either your private or public IP for the nimus node. If you use a public IP, you need to update the security group.  If you use a private IP, you need to be running from within the subnet.
6. You should now switch into the source directory of either the Luwak or Elasticsearch topology and build the topology, e.g.
```
cd /home/ubuntu/straw/src/luwak_search
mvn clean
mvn package
```
7. Finally, you can submit the topology to the cluster (whose nimbus node was specified in step 5) by executing
```
./submit_topology.sh
```


### Configuring Redis
Install redis on same server as UI and modify the bind interface redis conf -- set bind 0.0.0.0.
```
sudo apt-get install redis-server
sudo vi /etc/redis/redis.conf
```
If you want to use a seperate redis instance for benchmarking, you should repeat the above step on a different AWS machine.  [FEATURE: Add the redis config to the deployment scripts.]


