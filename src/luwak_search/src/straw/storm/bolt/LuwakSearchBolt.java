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
package straw.storm.bolt;



import java.io.IOException;
import java.util.Map;
import java.util.Timer;

import org.apache.lucene.analysis.standard.StandardAnalyzer;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import straw.storm.util.Counter;
import straw.storm.util.LuwakHelper;
import straw.storm.util.RequestsHelper;
import straw.storm.util.ScheduledMessageCounter;
import uk.co.flax.luwak.InputDocument;
import uk.co.flax.luwak.Matches;
import uk.co.flax.luwak.Monitor;
import uk.co.flax.luwak.MonitorQuery;
import uk.co.flax.luwak.QueryMatch;
import uk.co.flax.luwak.matchers.SimpleMatcher;
import uk.co.flax.luwak.presearcher.TermFilteredPresearcher;
import uk.co.flax.luwak.queryparsers.LuceneQueryParser;
import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;


/**
 * This bolt aggregates counts from multiple upstream bolts.
 */
public class LuwakSearchBolt extends BaseRichBolt {

	private OutputCollector collector;
	private Map conf;
	private static JedisPool pool;
	private Monitor monitor;
	private Counter counter;
	
	@SuppressWarnings("rawtypes")
	@Override
	public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
		this.conf = conf;
		this.collector = collector;
		
		// prepare the redis client
		pool = new JedisPool(new JedisPoolConfig(), conf.get("redis_host").toString());
		
		// count message throughput
		counter = new Counter();
		ScheduledMessageCounter message_counter = new ScheduledMessageCounter(counter, conf);
		Timer time = new Timer(); // Instantiate Timer Object
		time.schedule(message_counter, 0, 10000); // Create Repetitively task for every 30 secs
		
		// luwak
		try {
			this.monitor = new Monitor(new LuceneQueryParser("text", new StandardAnalyzer()), new TermFilteredPresearcher());
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	@Override
	public void execute(Tuple tuple) {

		// process the tuple
		String sourcename = tuple.getSourceComponent();
		String data = tuple.getValue(0).toString();

		// either we get a query and we need to add it to the index
		// or we get a document and we need to do a search
		// Values("query", request_id, user_id, query_id, query)
		// Values("document", source, document)
		if(sourcename.toLowerCase().contains("query")){
			// add queries
			MonitorQuery query = LuwakHelper.make_query(data);

			//register the query
			try {
				// System.out.println(query.toString());
				monitor.update(query);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
		else if (sourcename.toLowerCase().contains("document")){
			// try to parse as document
			String text = LuwakHelper.extract_text(data);

			//Build a document to check against the percolator
			InputDocument doc = null;
			if (text != null){
				doc = InputDocument.builder(RequestsHelper.generate_unique_identifier(data))
	                    .addField("text", text, new StandardAnalyzer())
	                    .build();
			}
			
			// pass the document through Luwak
			if (doc != null) {
				try {
					Matches<QueryMatch> matches = monitor.match(doc, SimpleMatcher.FACTORY);
					
					// we completed a search, so we need to inform the counter
					counter.count+=1;
					
					//Handle the result which is the set of queries in the percolator
					for(QueryMatch match : matches) {
						// System.out.println("Query: " + match.toString() + " matched document " + text);
						// emit results
						collector.emit(new Values(data));
						
						// publish the result to jedis
				        try (Jedis jedis_client = pool.getResource()) {
				        	jedis_client.publish(match.getQueryId(), text);
				        }
						
					}
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}

		// acknowledge 
		collector.ack(tuple);
	}


	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer) {
		declarer.declare(new Fields("document"));
	}

	@Override
	public void cleanup() {
		pool.destroy();
	}


}
