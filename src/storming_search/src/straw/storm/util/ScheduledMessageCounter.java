package straw.storm.util;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Map;
import java.util.TimerTask;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;


/*
 * 
 * This task can be used to log throughput count at a point in time.
 * It consumes a counter object, logs the counters value, then resets that value.
 * It should be passed to a scheduler.
 * 
 */
public class ScheduledMessageCounter extends TimerTask {

	private Counter counter;
	private SimpleDateFormat tfmt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SSS");
	private JedisPool pool;
	
	public ScheduledMessageCounter(Counter counter, Map conf){
		super();
		this.counter = counter;
		pool = new JedisPool(new JedisPoolConfig(), conf.get("redis_analytics_host").toString());
	}
	
	@Override
	public void run() {
		String time_stamp = tfmt.format(Calendar.getInstance().getTime());
		String msg = String.format("(%s, %s, %d)", time_stamp, counter.hashCode(), counter.count);
		
		// publish the result to jedis analytics db
        try (Jedis jedis_client = pool.getResource()) {
        	jedis_client.rpush("percolator", msg);
        }
		
		// reset counter
		counter.count=0;
	}
	
}
