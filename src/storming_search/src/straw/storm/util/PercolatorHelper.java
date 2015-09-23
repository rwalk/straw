package straw.storm.util;

import static org.elasticsearch.index.query.QueryBuilders.termsQuery;

import java.io.IOException;

import org.elasticsearch.common.xcontent.XContentBuilder;
import org.elasticsearch.common.xcontent.XContentFactory;
import org.elasticsearch.index.query.QueryBuilder;
import org.json.JSONArray;
import org.json.JSONObject;

public class PercolatorHelper {

	public static XContentBuilder make_document(String data) {
		// parse input JSON
		// JSONObject obj = null;
		String text = data.replace("{", "").replace("}", "");
//		try {
//			obj = new JSONObject(data);
//			text = obj.getString("text");	
//		} 
//		catch (org.json.JSONException e) {
//			System.out.println("JSON PARSER FAILED TO HANDLE: " + data);
//			//e.printStackTrace();
//		}
		
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
		return docBuilder;
	}
	
	public static QueryBuilder make_query(String data){
		// build a query out of the data JSON string
		QueryBuilder qb = null;
		JSONObject obj = null;
		try {
			obj = new JSONObject(data);
		} 
		catch (org.json.JSONException e) {
			System.out.println("JSON PARSER FAILED TO HANDLE: " + data);
			e.printStackTrace();
		}
			
		String type = obj.getString("type");
		
		// terms query parser
		if(type.equalsIgnoreCase("terms-query")) {
			Integer minimum_match = obj.getInt("minimum-match");
			JSONArray arr = obj.getJSONArray("terms");
			
			if (arr!=null){
				String[] string_arry = new String[arr.length()];
				// use length of array if minimum match not provided
				if (minimum_match==null){
					minimum_match=arr.length();
				}
				for(int i=0; i<arr.length(); i++){
					string_arry[i] = arr.getString(i);
				}
				qb = termsQuery("text", string_arry).minimumMatch(minimum_match);
			}
		}
		return qb; 
	}
}
