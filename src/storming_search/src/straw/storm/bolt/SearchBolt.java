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

import backtype.storm.Config;
import backtype.storm.task.OutputCollector;
import backtype.storm.task.TopologyContext;
import backtype.storm.topology.OutputFieldsDeclarer;
import backtype.storm.topology.base.BaseRichBolt;
import backtype.storm.tuple.Fields;
import backtype.storm.tuple.Tuple;
import backtype.storm.tuple.Values;

import org.apache.log4j.Logger;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.io.IOException;

// http client library
import java.io.InputStream;
import java.io.UnsupportedEncodingException;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.*;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.Consts;
import org.apache.http.Header;
import org.apache.http.HttpHost;
import org.apache.http.HttpRequest;
import org.apache.http.HttpResponse;
import org.apache.http.ParseException;
import org.apache.http.client.CookieStore;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.config.AuthSchemes;
import org.apache.http.client.config.CookieSpecs;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.config.ConnectionConfig;
import org.apache.http.config.MessageConstraints;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.config.SocketConfig;
import org.apache.http.conn.DnsResolver;
import org.apache.http.conn.HttpConnectionFactory;
import org.apache.http.conn.ManagedHttpClientConnection;
import org.apache.http.conn.routing.HttpRoute;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.DefaultHttpResponseFactory;
import org.apache.http.impl.client.BasicCookieStore;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.DefaultHttpResponseParser;
import org.apache.http.impl.conn.DefaultHttpResponseParserFactory;
import org.apache.http.impl.conn.ManagedHttpClientConnectionFactory;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.impl.conn.SystemDefaultDnsResolver;
import org.apache.http.impl.io.DefaultHttpRequestWriterFactory;
import org.apache.http.io.HttpMessageParser;
import org.apache.http.io.HttpMessageParserFactory;
import org.apache.http.io.HttpMessageWriterFactory;
import org.apache.http.io.SessionInputBuffer;
import org.apache.http.message.BasicHeader;
import org.apache.http.message.BasicLineParser;
import org.apache.http.message.LineParser;
import org.apache.http.ssl.SSLContexts;
import org.apache.http.util.CharArrayBuffer;
import org.apache.http.util.EntityUtils;
import org.elasticsearch.ElasticsearchException;
import org.elasticsearch.action.percolate.PercolateResponse;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.elasticsearch.common.xcontent.XContentBuilder;
import org.elasticsearch.common.xcontent.XContentFactory;
import org.elasticsearch.index.query.QueryBuilder;
import org.elasticsearch.common.settings.ImmutableSettings;
import org.elasticsearch.common.settings.Settings;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;
import straw.storm.util.PercolatorHelper;
import straw.storm.util.RequestsHelper;
import static org.elasticsearch.index.query.QueryBuilders.*;
import static org.elasticsearch.index.query.FilterBuilders.*;
import static org.elasticsearch.common.xcontent.XContentFactory.*;


/**
 * This bolt aggregates counts from multiple upstream bolts.
 */
public class SearchBolt extends BaseRichBolt {

	private OutputCollector collector;
	private Map conf;
	private TransportClient client;
	private static JedisPool pool; 
	private Jedis jedis_client;
	
	@SuppressWarnings("rawtypes")
	@Override
	public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
		this.conf = conf;
		this.collector = collector;
		SearchBolt.pool = new JedisPool(new JedisPoolConfig(), conf.get("redis_host").toString());
		this.jedis_client = pool.getResource();
		// prepare the search engine
		String host = conf.get("elasticsearch_host").toString();
		int port = Integer.parseInt(conf.get("elasticsearch_port").toString());	  
		Settings settings = ImmutableSettings.settingsBuilder().put("cluster.name", "rwalker-elasticsearch-cluster").build();
		client = new TransportClient(settings)
		.addTransportAddress(new InetSocketTransportAddress(host, port));
		
		// prepare the redis client
	}

	@Override
	public void execute(Tuple tuple) {

		// process the tuple recieved from kafka
		String sourcename = tuple.getSourceComponent();
		String data = tuple.getValue(0).toString();


		// either we get a query and we need to add it to the index
		// or we get a document and we need to do a search
		// Values("query", request_id, user_id, query_id, query)
		// Values("document", source, document)
		if(sourcename.toLowerCase().contains("query")){
			System.out.println(data);
			// add queries
			QueryBuilder query = PercolatorHelper.make_query(data);

			//register the query in the percolator
			if (query != null ) {
				try {
					client.prepareIndex(conf.get("index_name").toString(), ".percolator", RequestsHelper.generate_unique_identifier(data))
					.setSource(jsonBuilder()
							.startObject()
							.field("query", query) // Register the query
							.field("format", "objects")
							.endObject())
							.setRefresh(true) // Needed when the query shall be available immediately
							.execute().actionGet();
				} catch (ElasticsearchException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}

				System.out.println("QUERY: " + query.toString());
			}
		}
		else if (sourcename.toLowerCase().contains("document")){
			// try to parse as document
			String text = PercolatorHelper.extract_text(data);
		
			//Build a document to check against the percolator
		    XContentBuilder docBuilder = null;
			if (text != null){
				try {
					docBuilder = XContentFactory.jsonBuilder().startObject();
				    docBuilder.field("doc").startObject(); //This is needed to designate the document
				    docBuilder.field("text", text);
				    docBuilder.endObject(); //End of the doc field
				    docBuilder.endObject(); //End of the JSON root object
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
				
			if (docBuilder != null) {
			//Percolate
			PercolateResponse response = client.preparePercolate()
					.setIndices(conf.get("index_name").toString())
					.setDocumentType(conf.get("document_type").toString())
					.setSource(docBuilder).execute().actionGet();

				//Handle the result which is the set of queries in the percolator
				for(PercolateResponse.Match match : response) {
					System.out.println("Query: " + match.getId().toString() + " matched document " + text);
					// emit results
					collector.emit(new Values(data));
					jedis_client.publish(match.getId().toString(), text);					
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
		client.close();
		pool.destroy();
	}


}
