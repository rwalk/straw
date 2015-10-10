# straw
A platform for real-time streaming search

The goal of this project is to provide a clean, scalable architecture for real-time search on streaming data.  Additionally, the project contains utilities to provide some very simple throughput benchmarking of Elasticsearch Percolators vs Lucence-Luwak.  Preliminary benchmarks may be found in:

http://straw.ryanwalker.us/about

Comments and critiques about these benchmarks are greatly appreciated!

This project was inspired by the following excellent blog posts on streaming search: 
- http://www.confluent.io/blog/real-time-full-text-search-with-luwak-and-samza/
- http://www.flax.co.uk/blog/2015/07/27/a-performance-comparison-of-streamed-search-implementations/

I completed this project as a Fellow in the 2015C Inisght Data Engineering Silicon Valley program.

## Architechture
The core of the platform is an Apache Storm cluster which parallelizes the work of real-time streaming search.  Internally, the Storm cluster consumes messages from a Kafka cluster and these messages are distributed to bolts which each contain a Lucene-Luwak index.  The project contains a demo flask UI which handles subscriptions with a Redis PUBSUB system.

More about the architecture can be found at:
http://straw.ryanwalker.us/about

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

Steps:
1) cd src/aws_config
2) run ./create_clusters.py --help to get instructions about this AWS creation script and follow instructions.  You may
wish to edit a few things in this file, such as the tag_prefix which gives a unique custom prefix to each service.
3) src/aws_config/configure contains scripts to configure each of the individual services; you'll need to run each of these to configure the resource.

Once resources are created, you can run
```
./discover.py
```
NOTE: You should modify the tag-prefix in this file to match the tag prefix you've set elsewhere. [FEATURE: Tag should be set in a GLOBAL CONFIG file.]

### Configuring Redis
Install redis on same server as UI and modify the bind interface redis conf -- set bind 0.0.0.0.
```
sudo apt-get install redis-server
sudo vi /etc/redis/redis.conf
```
If you want to use a seperate redis instance for benchmarking, you should repeat the above step on a different AWS machine.  [FEATURE: Add the redis config to the deployment scripts.]


