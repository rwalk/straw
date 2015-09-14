#!/usr/bin/python3
import boto3
from botocore.exceptions import ClientError as BotoClientError

# instance filters
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['stopped']}]

if __name__=="__main__":

    # create the VPC (Virtual Private Cloud)

    # remove existing vpc if possible
    for v in ec2.vpcs.filter(Filters=[{'Name':'tag-value','Values':['rwalker-vpc']}]):
        try:
            v.delete()
        except(BotoClientError) as e:
            print("Couldn't delete the VPC with id={0}. {1}".format(v.id, e))
            
    # create the vpc
    my_vpc = ec2.create_vpc(CidrBlock='10.0.0.0/27')
    vpc = ec2.Vpc(my_vpc.id)
    vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsSupport={'Value':True})
    vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsHostnames={'Value':True})
    vpc.create_tags(Tags=[{'Key':'Name', 'Value':'rwalker-vpc'}])

    # subnets
    subnet = vpc.create_subnet(CidrBlock='10.0.0.0/27')

    # gateways
    gateway = ec2.create_internet_gateway()
    gateway.attach_to_vpc(VpcId=vpc.id)
    
    

    
