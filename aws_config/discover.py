#!/usr/bin/python3
#
#   Discover straw cluster resources running on AWS
#
import boto3, argparse
from create_clusters import services, get_tag

if __name__=="__main__":
    
    # argument help
    parser = argparse.ArgumentParser(description='Discover AWS ec2 instances for the straw cluster.')
    args = parser.parse_args()

    # boto3
    ec2 = boto3.resource('ec2')
    client= boto3.client('ec2')

    for v in ec2.instances.filter(Filters=[{'Name':'tag-value','Values':[get_tag(s+'-node') for s in services]}]):
        print("SERVICE: {0:<15}\tID: {1:<15}\tIP: {2:<15}".format(v.tags[0]['Value'], v.instance_id, v.public_ip_address))

