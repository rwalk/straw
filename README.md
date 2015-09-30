# straw
A platform for real-time streaming search

The goal of this project is to provide a clean, scalable architecture for real-time search on a stream.

Some great resources on streaming search:
- http://www.confluent.io/blog/real-time-full-text-search-with-luwak-and-samza/
- http://www.flax.co.uk/blog/2015/07/27/a-performance-comparison-of-streamed-search-implementations/

## What's included:
- Automated AWS deployment utilities in AWS_CONFIG using boto3.  Automatically deploy and configure clusters to run streaming search
- Java based Storm implementation:
  - KafkaSpout for query and document spouts
  - Two flavors of search bolts, one for Elasticsearch-Percolators and one for Lucene with Luwak
  - Storm toplogy for streaming search and configuration management
- Scripts to stage document data, including twitter API sampling
- Testing and other utilities, including Docker components so that the entire topology can run on a local machine
