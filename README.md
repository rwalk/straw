# straw
A platform for real-time streaming search

The goal of this project is to provide a clean, scalable architecture for real-time search on streaming.

Some great resources on streaming search:
- http://www.confluent.io/blog/real-time-full-text-search-with-luwak-and-samza/
- http://www.flax.co.uk/blog/2015/07/27/a-performance-comparison-of-streamed-search-implementations/

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
