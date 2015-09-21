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
import straw.storm.bolt.StreamingSearchBolt;
import straw.storm.spout.StreamingSearchSpout;
import straw.storm.util.ConfigurationManager;
import org.elasticsearch.*;

// configuration
import java.io.FileNotFoundException;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Date;
import java.util.Properties;

/**
 * This is a basic example of a Storm topology, following the example
 * https://github.com/buildlackey/cep/tree/master/storm%2Bkafka
 * 
 */
public class StreamingSearchTopology {

  public static void main(String[] args) throws Exception {
    TopologyBuilder builder = new TopologyBuilder();

    builder.setSpout("streaming-search-spout", new StreamingSearchSpout(), 1);
    builder.setBolt("streaming-search-bolt", new StreamingSearchBolt(), 1).shuffleGrouping("streaming-search-spout");

    // configuration
    ConfigurationManager config_manager = new ConfigurationManager();
    config_manager.put("stream_file", "example_file");
    config_manager.put("elasticsearch_host", "elasticsearch_host");
    config_manager.put("elasticsearch_port", "elasticsearch_port");
    config_manager.put("index_name", "index_name");
    config_manager.put("document_type", "document_type");
    Config config = config_manager.get();
    
    if (args != null && args.length > 0) {
      config.setNumWorkers(3);
      StormSubmitter.submitTopologyWithProgressBar(args[0], config, builder.createTopology());
    }
    else {
      LocalCluster cluster = new LocalCluster();
      cluster.submitTopology("streaming-search-topology", config, builder.createTopology());
      
      // run for a while then die
      Utils.sleep(20000);
      cluster.killTopology("streaming-search-topology");
      cluster.shutdown();
    }
  }
}
