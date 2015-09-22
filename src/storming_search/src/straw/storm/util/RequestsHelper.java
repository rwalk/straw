package straw.storm.util;

import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class RequestsHelper {

	public static String generate_unique_identifier(String object_string){
		
		// generate a unique id for string representation of an object
	    MessageDigest md;
		byte[] hash = null;
		try {
			md = MessageDigest.getInstance("MD5");
			hash = md.digest(object_string.getBytes("UTF-8"));
		} catch (NoSuchAlgorithmException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	    
	    //converting byte array to Hexadecimal String
	   StringBuilder sb = new StringBuilder(2*hash.length);
	   for(byte b : hash){
	       sb.append(String.format("%02x", b&0xff));
	   }
	   return sb.toString();
	}
	
}
