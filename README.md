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
4. run `mvn package`
5. `./run_search_topology.sh` [BUG: You need to push lots of documents to Kafka or you'll get an error]
6. In a seperate terminal, activate the frontend by calling ./run.py from src/frontend

### Deploy to AWS
#### Prequesites:

1. Install the aws cli
2. Install Python boto3
3. Set your default configurations by calling "aws configure"
4. Modify the settings in `straw_service_config.sh` to your own AWS account information and then
```
source straw_service_config.sh
```

####Steps:

1. `cd src/aws_config`
2. `/create_clusters.py --help` to get instructions about this AWS creation script and follow instructions.
3. Once all resources are created, `cd configure`. This directory contains scripts to configure each of the individual services; you'll need to run each of these to configure the resource, e.g. `./configure_elasticsearch`.
4. Once resources are created, run
```
./discover.py
```
to see the list of services and their IPs.

####Submitting topologies
To submit or run topologies, you need to install storm on your machine (or, even better, on a dedicted machine within the subnet of the Storm cluster).  Install storm as follows:
```
sudo apt-get update
sudo apt-get install openjdk-7-jdk
wget http://mirrors.gigenet.com/apache/storm/apache-storm-0.9.5/apache-storm-0.9.5.tar.gz -P ~/Downloads
sudo tar zxvf ~/Downloads/apache-storm*.gz -C /usr/local
sudo mv /usr/local/apache-storm* /usr/local/storm
```
Then edit `/usr/local/storm/config/storm.yaml` by adding the line
```nimbus.host: 10.X.X.X```
using either your private or public IP for the nimbus node. If you use a public IP, you need to update the security group.  If you use a private IP, you need to be running from within the subnet.

Next, you need to tell storm where all of your cluster resources reside.  To do this,
```
vi straw/config/config.properties
```
Enter the private IPs of your system resources, following this template.  We are assuming that all of the resources live on the same subnet in the cluster.

You should now switch into the source directory of either the Luwak or Elasticsearch topology and build the topology, e.g.
```
cd /home/ubuntu/straw/src/luwak_search
mvn clean
mvn package
```
Finally, you can submit the topology to the cluster (whose nimbus node was specified in step 5) by executing
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

## Benchmarking and simulation
A goal of straw project was to allow for benchmarking of the Lucene-Luwak package in a distributed context.  

### Measuring throughput
I measure throughput through the search bolts of the Storm cluster in simple way.  Start a stopwatch in a background thread.  Each bolt has a counter which get incremented each time a document gets checked against the search engine.  When the stopwatch hits 10 seconds, collect the data from each counter, publish the result to a redis DB, and reset the counter.

### Generating/simulating data
For benchmarking and simulations, you'll need a way to generate tweets and queries. For this purpose, I've added many tools to the `straw/utils` directory.  In particular, the scripts
```
./kafka_add_documents
./kafka_add_queries
```
can be used to add documents and queries from sample files.  Some small example data files are found in ```straw/data```.  For long running simultion, you can run ```./kafka_add_documents.sh``` in a cronjob, to periodically put documents into the Kafka cluster.  NOTE: Kafka has been configured to purge documents after 1 hour.

You can easily harvest your own tweet data from the Twitter api. Try the following helper script which uses Twython to read from the Twitter streaming sample API:
```
./tweet_sampler.py --help
```
You'll need to export your twitter credentials as inviornment variables to run this and other scripts, e.g.
```
source my_twitter_credentials
```
where `my_twitter_credentials` looks like
```
export TWITTER_ACCESS_TOKEN=...
export TWITTER_SECRET_TOKEN=...
export TWITTER_CONSUMER_TOKEN=...
export TWITTER_CONSUMER_SECRET=...

```
To generate reasonably complex queries, the included query maker utility might be helpful
```
./query_maker.py --help
```
this script takes a sample of tweets and uses NLTK to compute bigram frequencies.  The most frequent bigram are then converted into queries that Straw can parse.  For ease of use, I've included `data/queries.bigrams` in  the repo.  This is a collection of 100,000 generated bigram queries collected from a sample of 20 million tweets.

