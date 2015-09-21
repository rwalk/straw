
/*
 * 
 * This class is a simple wrapper around the storm configuration object.
 * For straw, we store all configuration in a config file whose location is 
 * given by the value of the enviornment variable STRAW_CONFIG.
 * 
 * The purpose of this class is to allow for a simple interface where
 * we can ask storm to set a configuration value "storm_property" based on 
 * the value of "system_name" in the STRAW_CONFIG file.  An error is thrown
 * when the "system_name" is not found in the config file.
 * 
 */
package straw.storm.util;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.Properties;
import backtype.storm.Config;

public class ConfigurationManager {

	private Map<String, String> env = System.getenv();
	private String config_filename;
	private Properties prop = new Properties();
	private Config config = new Config();
	
	public ConfigurationManager() {		
		// read config file location from sys
		config_filename = env.get("STRAW_CONFIG");
	    if(config_filename==null)
	    {
	    	throw new RuntimeException("Couldn't access config file, did you set STRAW_CONFIG in enviornment?");
	    }

	    // load the properties
	    InputStream input = null;
	    try {
			input = new FileInputStream(config_filename);
			prop.load(input);
		} catch (IOException ex) {
			ex.printStackTrace();
		} finally {
			if (input != null) {
				try {
					input.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	    
	}
	
	// add a setting to the config
	public void put(String storm_property, String system_name){
		if (prop.getProperty(system_name)==null){
			throw new RuntimeException("Property "+system_name+" not found in config file " + config_filename +".");
		}
		config.put(storm_property, prop.getProperty(system_name));
	}
	
	// return the storm config object
	public Config get(){
		return config;
	}
}
