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
import java.util.Map;
import java.util.Random;

import org.json.JSONObject;


public class DocumentSpout extends BaseRichSpout {
  SpoutOutputCollector collector;
  private FileReader fileReader;
  private boolean completed = false;
  private Map conf;


  @Override
  public void open(Map conf, TopologyContext context, SpoutOutputCollector collector) {
    try {
    	this.fileReader = new FileReader(conf.get("document_file").toString());
    } catch (FileNotFoundException e) {
    	throw new RuntimeException("Error reading file "+conf.get("stream_file"));
    }
    this.conf = conf;
    this.collector = collector;
  }

  @Override
  public void nextTuple() {
	  
	// put some slack in the pipeline for initial development
    Utils.sleep(10);
    String str, msg;
    
    // once the file is done reading, we just start over again
    if(completed){
        try {
        	this.fileReader = new FileReader(conf.get("stream_file").toString());
        } catch (FileNotFoundException e) {
        	throw new RuntimeException("Error reading file "+conf.get("stream_file"));
        }
        completed = false;
    }
    
    // buffered read from the file
    BufferedReader reader = new BufferedReader(fileReader);
    try {
    	while((str=reader.readLine())!= null) {
    		
    		JSONObject obj = new JSONObject(str);
    		msg = obj.getString("text");
    		if( msg != null){
    			this.collector.emit(new Values("document", msg));
    		}
    	}
    } catch(Exception e) {
    	throw new RuntimeException("Error reading tuple.", e);
    } finally {
    	completed = true;
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
    declarer.declare(new Fields("kind","value"));
  }

}