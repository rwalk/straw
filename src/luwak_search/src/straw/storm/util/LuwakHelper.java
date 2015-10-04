package straw.storm.util;



import org.apache.commons.lang.StringUtils;

import org.json.JSONArray;
import org.json.JSONObject;

import uk.co.flax.luwak.MonitorQuery;

public class LuwakHelper {

	public static String extract_text(String data) {
		// parse input JSON
		JSONObject obj;
		String text = null;
		try {
			obj = new JSONObject(data);
			text = obj.getString("text");
		} 
		catch (org.json.JSONException e) {
			// TODO: Bad json passed
			// System.out.println("JSON PARSER FAILED TO HANDLE: " + data);
			//e.printStackTrace();
		}
		
		return text;
	}
	
	public static MonitorQuery make_query(String data){
		// build a query out of the data JSON string
		MonitorQuery qb = null;
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
				// query is lucene style, e.g. "text:term1 AND text:term2 ... "
				qb = new MonitorQuery(RequestsHelper.generate_unique_identifier(data), "text:" + StringUtils.join(string_arry, " AND text:"));
			}
		}
		return qb; 
	}
}
