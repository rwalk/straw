#!/usr/bin/python3
#
#   Put documents from the stream into Kafka
#
import argparse
from kafka import KafkaConsumer

if __name__=="__main__":

    # arg parsing
    parser = argparse.ArgumentParser(description="Consume messages from kafka.")
    parser.add_argument("host", help="A Kafka host")
    parser.add_argument("topic", help="A topic to consume")
    parser.add_argument("-p","--port", default="9092", help="A Kafka port, default 9092.")   
    args = parser.parse_args()

    # get a client
    #consumer = KafkaConsumer('documents', group_id='straw', bootstrap_servers=["{0}:{1}".format(args.host, args.port)])
    print("Trying to get messages from topic {0} on {1}:{2}".format(args.topic, args.host, args.port))
    consumer = KafkaConsumer(args.topic, bootstrap_servers=["{0}:{1}".format(args.host, args.port)], auto_offset_reset='smallest')

    # read through the file and send messages to Kafka in chunks
    for message in consumer:
        # message value is raw byte string -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print("{0}:{1}:{2}: key={3} value={4}".format(message.topic, message.partition,
                                             message.offset, message.key,
                                             message.value.decode('utf-8')))


            
