/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package straw.storm;

import backtype.storm.Config;
import backtype.storm.LocalCluster;
import backtype.storm.StormSubmitter;
import backtype.storm.spout.SchemeAsMultiScheme;
import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.testing.TestWordSpout;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.TopologyBuilder;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;
import backtype.storm.utils.Utils;

import java.util.Map;

import storm.kafka.*;
import straw.storm.bolt.SearchBolt;
import straw.storm.spout.DocumentSpout;
import straw.storm.spout.QuerySpout;
import straw.storm.util.ConfigurationManager;

import org.elasticsearch.*;

// configuration
import java.io.FileNotFoundException;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Properties;

/**
 * This is a basic example of a Storm topology, following the example
 * https://github.com/buildlackey/cep/tree/master/storm%2Bkafka
 * 
 */
public class StreamingSearchTopology {

  public static void main(String[] args) throws Exception {
	/*
	 *   Define and packaged a topology to submit to a storm cluster  
	 */
	 
	  
	/*
	 * CONFIGURATION
	 * TODO: Better config management; should throw meaningful errors
	 * when a config value is called but not defined.
	 * 
	 */
    ConfigurationManager config_manager = new ConfigurationManager();
    config_manager.put("stream_file", "example_file");
    config_manager.put("elasticsearch_host", "elasticsearch_host");
    config_manager.put("elasticsearch_port", "elasticsearch_port");
    config_manager.put("index_name", "index_name");
    config_manager.put("document_type", "document_type");
    config_manager.put("kafka_query_topic", "kafka_query_topic");
    config_manager.put("kafka_document_topic", "kafka_document_topic");
    config_manager.put("zookeeper_hosts", "zookeeper_hosts");
    config_manager.put("redis_host", "redis_host");
    config_manager.put("redis_port", "redis_port");
    
    Config config = config_manager.get();
    
    /*
     * KafkaSpout configuration
     */
       
    // offset management
    String zkroot = "/brokers"; // the root path in Zookeeper for the spout to store the consumer offsets
    String zkid = "ids"; // an id for this consumer for storing the consumer offsets in Zookeeper
    
    // set zookeeper host
    BrokerHosts brokerHosts = new ZkHosts("localhost:2181", zkroot);
    
    // kafka topics
    String query_topic = config.get("kafka_query_topic").toString();
    String document_topic = config.get("kafka_document_topic").toString();
    
    // define spouts
    SpoutConfig query_spout_config = new SpoutConfig(brokerHosts, query_topic, zkroot, zkid);
    query_spout_config.forceFromStart=true;
    SpoutConfig document_spout_config = new SpoutConfig(brokerHosts, document_topic, zkroot, zkid);
    document_spout_config.forceFromStart=true;
    
    // add a string scheme to the spouts
    document_spout_config.scheme = new KeyValueSchemeAsMultiScheme(new StringKeyValueScheme());
    query_spout_config.scheme = new KeyValueSchemeAsMultiScheme(new StringKeyValueScheme());
    
    // topology definition
    TopologyBuilder builder = new TopologyBuilder();
    builder.setSpout("query-spout", new KafkaSpout(query_spout_config), 1);
    builder.setSpout("document-spout", new KafkaSpout(document_spout_config), 1);
    builder.setBolt("search-bolt", new SearchBolt(), 1)
    	.allGrouping("query-spout")
    	.shuffleGrouping("document-spout");
    	
    // topology submission
    if (args != null && args.length > 0) {
      config.setNumWorkers(3);
      StormSubmitter.submitTopologyWithProgressBar(args[0], config, builder.createTopology());
    }
    else {
      LocalCluster cluster = new LocalCluster();
      cluster.submitTopology("streaming-search-topology", config, builder.createTopology());
      
      // run for a while then die
      Utils.sleep(50000000);
      cluster.killTopology("streaming-search-topology");
      cluster.shutdown();
      
    }
  }
}
