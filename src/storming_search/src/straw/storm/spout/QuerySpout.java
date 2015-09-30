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
package straw.storm.spout;

import backtype.storm.spout.SpoutOutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichSpout;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Values;
import backtype.storm.utils.Utils;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.security.MessageDigest;
import java.util.Map;
import java.util.Random;

import org.json.JSONObject;

import straw.storm.util.RequestsHelper;


public class QuerySpout extends BaseRichSpout {
  SpoutOutputCollector collector;
  private FileReader fileReader;

  @Override
  public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
    try {
    	this.fileReader = new FileReader(conf.get("query_file").toString());
    } catch (FileNotFoundException e) {
    	throw new RuntimeException("Error reading file "+conf.get("query_file"));
    }
    this.collector = collector;
  }

  @Override
  public void nextTuple() {
	  
	// put some slack in the pipeline for initial development
    String str, query, user_id, query_id, request_id;
    
    // buffered read from the file
    BufferedReader reader = new BufferedReader(fileReader);
    try {
    	while((str=reader.readLine())!= null) {
    		JSONObject obj = new JSONObject(str);
    		query = obj.getString("query");
    		user_id = obj.getString("user");
    		request_id = RequestsHelper.generate_unique_identifier(str);
    		query_id = RequestsHelper.generate_unique_identifier(query);
    		
			if( query != null){
				this.collector.emit(new Values("query", request_id, user_id, query_id, query));
			}
			
    	}
    } catch(Exception e) {
    	throw new RuntimeException("Error reading query.", e);
    }
  }

  @Override
  public void ack(Object id) {
  }

  @Override
  public void fail(Object id) {
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
	  declarer.declare(new Fields("kind","request_id", "user_id", "query_id", "query"));
  }

}