#!/usr/bin/python3
'''
STEPS:
    Load numbered records into Kafka
    Run streaming search over the records with redis connnection listenning in the background.
    Measure time between numbered events
'''
import argparse
from datetime import datetime
from kafka import SimpleProducer, KafkaClient

BENCHMARK_MESSAGE_TEXT="straw-benchmark-text"

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Benchmarking the straw platform.")
    parser.add_argument("file", help="Template messages file")
    parser.add_argument("n", help="Interval size, the number of messages between measurements")
    parser.add_argument("host", help="Public IP address of a Kafka node")
    parser.add_argument("topic", help="Kafka topic to feed")
    parser.add_argument("-r", "--repititions", default=100, help="Number of trials, default 100")
    parser.add_argument("-p", "--port", default=9092, help="port for zookeeper, default 9092")
    args = parser.parse_args()
    
    # read in example lines upto interval size - 2
    interval_block = []
    with open(args.file, "rb") as f:
        cnt = 0
        for l in f:
            interval_block.append(l)
            cnt+=1
            if cnt==int(args.n)-1:
                break

    # get a client
    print("Connecting to Kafka node {0}:{1}".format(args.host, args.port))
    kafka = KafkaClient("{0}:{1}".format(args.host, args.port))
    producer = SimpleProducer(kafka)
    
    # post messages to kafka in batches 
    for i in range(int(args.repititions)):
        msg = "{{ \"text\": \"{0}, {1}\" }}".format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'), BENCHMARK_MESSAGE_TEXT)
        producer.send_messages(args.topic, *(interval_block + [msg.encode("utf-8")]))
        print("Sent {0} messages to kafka.".format(len(interval_block)+1))
        
            
            
            





