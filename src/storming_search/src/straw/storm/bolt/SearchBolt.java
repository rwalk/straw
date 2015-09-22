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

import static org.elasticsearch.index.query.QueryBuilders.*;
import static org.elasticsearch.index.query.FilterBuilders.*;
import static org.elasticsearch.common.xcontent.XContentFactory.*;


/**
 * This bolt aggregates counts from multiple upstream bolts.
 */
public class StreamingSearchBolt extends BaseRichBolt {

  private OutputCollector collector;
  private Map conf;
  private TransportClient client;
  private ArrayList<QueryBuilder> queries = new ArrayList<QueryBuilder>();
    
  @SuppressWarnings("rawtypes")
  @Override
  public void prepare(Map conf, TopologyContext context, OutputCollector collector) {
	  this.conf = conf;
	  this.collector = collector;
	  
	  // prepare the search engine
	  String host = conf.get("elasticsearch_host").toString();
	  int port = Integer.parseInt(conf.get("elasticsearch_port").toString());	  
	  client = new TransportClient()
			  .addTransportAddress(new InetSocketTransportAddress(host, port));

	  // add queries to the list
	  queries.add(termsQuery("text", "Justin","Bieber").minimumMatch(2));
	  queries.add(termsQuery("text", "facebook","acquires").minimumMatch(2));
	  queries.add(termsQuery("text", "google","acquires").minimumMatch(2));
	  queries.add(termsQuery("text", "free","money").minimumMatch(2));
	  queries.add(termsQuery("text", "legion","doom").minimumMatch(2));
	  queries.add(termsQuery("text", "zebra","xylaphone","ham","coffee","toast","legume").minimumMatch(1));
	  
	  //register the queries in the percolator
	  for(int i=0; i<queries.size(); i++ ) {
		  try {
			client.prepareIndex(conf.get("index_name").toString(), ".percolator", "q"+Integer.toString(i))
			      .setSource(jsonBuilder()
			          .startObject()
			              .field("query", queries.get(i)) // Register the query
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
	  }
  }

  @Override
  public void execute(Tuple tuple) {
    String kind = tuple.getString(0);
    String document = tuple.getString(1);
    
    //Build a document to check against the percolator
    XContentBuilder docBuilder = null;
	try {
		docBuilder = XContentFactory.jsonBuilder().startObject();
	    docBuilder.field("doc").startObject(); //This is needed to designate the document
	    docBuilder.field("text", document);
	    docBuilder.endObject(); //End of the doc field
	    docBuilder.endObject(); //End of the JSON root object
	} catch (IOException e) {
		// TODO Auto-generated catch block
		e.printStackTrace();
	}

    //Percolate
    PercolateResponse response = client.preparePercolate()
                            .setIndices(conf.get("index_name").toString())
                            .setDocumentType(conf.get("document_type").toString())
                            .setSource(docBuilder).execute().actionGet();
    
    //Iterate over the results
    for(PercolateResponse.Match match : response) {
        //Handle the result which is the name of
        //the query in the percolator
    	System.out.println("Found a match for: " + document);
    	System.out.println("Query: " + match);
    }
    
    // emit results
    if(kind.equals("document")){
    	collector.emit(new Values(document));
    }
    
    // acknowledge 
    collector.ack(tuple);
  }

  @Override
  public void declareOutputFields(OutputFieldsDeclarer declarer) {
    declarer.declare(new Fields("document"));
  }
}
