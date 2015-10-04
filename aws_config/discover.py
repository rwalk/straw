#!/usr/bin/python3
#
#   Discover straw cluster resources running on AWS
#
import boto3, argparse
from create_clusters import services, get_tag

class ServicesList:
    '''Container class for AWS services info'''
    def __init__(self):
        ec2 = boto3.resource('ec2')
        client= boto3.client('ec2')
        filt=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name':'tag-value','Values':[get_tag(s+'-node') for s in services]}]
        self.services = []
        for v in ec2.instances.filter(Filters=filt):
            self.services.append(v)

    def print(self):
        for v in self.services:
            print("SERVICE: {0:<15}\tID: {1:<15}\tIP: {2:<15} PRIVATE IP: {3:<15}".format(v.tags[0]['Value'], 
                v.instance_id, v.public_ip_address, v.private_ip_address))

    def make_config_file(self, filename):
        '''create a straw config file for AWS'''

        def find_first_service(s):
            '''find the FIRST listed service with tag post-fix s
               NOTE: We implicitly assume that the list of AWS services is fixed.
               We should fix that by identifying the leader nodes among each service
               type.
            '''
            for v in self.services:
                if v.tags[0]['Value']==get_tag(s):
                    return(v.private_ip_address)

        with open(filename,"w") as f:
            header = """#
# config for straw.storm application
#

"""
            f.write(header)
            elasticsearch = """
# elasticsearch settings
elasticsearch_host={0}
elasticsearch_port=9300
elasticsearch_cluster_name={1}
index_name=documents
document_type=document
""".format(find_first_service("elasticsearch-node"), get_tag("elasticsearch-cluster"))
            f.write(elasticsearch)

            kafka = """
# kafka settings
zookeeper_host={0}
zookeeper_port=2181
kafka_query_topic=queries
kafka_document_topic=documents
""".format(find_first_service("kafka-node"))
            f.write(kafka)

            redis = """
# redis
redis_host={0}
redis_port=6379
""".format(find_first_service("flask-node"))
            f.write(redis)
        print("Wrote config file {0}.".format(f.name))

if __name__=="__main__":
    
    # argument help
    parser = argparse.ArgumentParser(description='Discover AWS ec2 instances for the straw cluster.')
    args = parser.add_argument("--configure", help="Write a configuration file", action="store_true")
    args = parser.parse_args()

    # boto3
    S = ServicesList()
    S.print()
    
    if args.configure:
        S.make_config_file("config.properties.tmp")
