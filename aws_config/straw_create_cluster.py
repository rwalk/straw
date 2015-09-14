#!/usr/bin/python3
#
#   Create the resources for Straw cluster on AWS
#
#   RUN aws configure prior to executing this script.

import boto3, os
from botocore.exceptions import ClientError as BotoClientError
from time import sleep

# configs
keyfile = "/home/ryan/projects/insight/accounts/rwalker.pem"
initfile = "base_kafka_image_config.sh"
tag_prefix = "rwalker-"
vpc_cidr = "10.0.0.0/27"
subnet_cidr = "10.0.0.0/27"         # we have just one subnet right now
number_instances=4
base_aws_image = 'ami-5189a661'
pemkey = 'rwalker'

def get_tag(name):
    return (tag_prefix + name)


if __name__=="__main__":

    # boto3 api: we oddly seem to need both ec2 resource and client
    ec2 = boto3.resource('ec2')
    client= boto3.client('ec2')

    #
    # create the VPC (Virtual Private Cloud)
    #

    # remove vpc if it already exists
    for v in ec2.vpcs.filter(Filters=[{'Name':'tag-value','Values':[get_tag('vpc')]}]):
        try:
            v.delete()
        except(BotoClientError) as e:
            print("Couldn't delete the VPC with id={0}. {1}".format(v.id, e))
            
    # create the vpc
    my_vpc = ec2.create_vpc(CidrBlock=vpc_cidr)
    vpc = ec2.Vpc(my_vpc.id)
    vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsSupport={'Value':True})
    vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsHostnames={'Value':True})
    vpc.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('vpc')}])

    #
    # Create a single subnet in vpc
    #
    # subnets
    for v in ec2.subnets.filter(Filters=[{'Name':'tag-value','Values':[get_tag('subnet')]}]):
        try:
            v.delete()
        except(BotoClientError) as e:
            print("Couldn't delete the subnet with id={0}. {1}".format(v.id, e))
    subnet = vpc.create_subnet(CidrBlock=subnet_cidr)
    subnet.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('subnet')}])

    
    #
    # Create a gateway and attach to vpc
    #
    gateway = ec2.create_internet_gateway()
    gateway.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('gateway')}])
    gateway.attach_to_vpc(VpcId=vpc.id)

    #
    #   Create a route table
    #
    
    for v in ec2.route_tables.filter(Filters=[{'Name':'tag-value','Values':[get_tag('route_table')]}]):
        try:
            v.delete()
        except(BotoClientError) as e:
            print("Couldn't delete the route table with id={0}. {1}".format(v.id, e))
    rt = ec2.create_route_table(VpcId=vpc.id)
    rt.associate_with_subnet(SubnetId=subnet.id)
    rt.create_route(GatewayId=gateway.id, DestinationCidrBlock='0.0.0.0/0')
    rt.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('route_table')}])


    #   
    #   Create a security group
    #
    for v in ec2.security_groups.filter(Filters=[{'Name':'group-name','Values':[get_tag('security-group')]}]):
        try:
            v.delete()
        except(BotoClientError) as e:
            print("Couldn't remove security group {0}. {1}".format(get_tag('security-group'), e))
    security_group = ec2.create_security_group(GroupName=get_tag('security-group'), 
        Description='A security group for straw clusters',
        VpcId=vpc.id)

    # permissions
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 0,
            'ToPort': 65535,
            'IpRanges': [
                {
                    'CidrIp': '10.0.0.0/16'
                },
            ],
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                },
            ],
        }
    ]
    security_group.authorize_egress(IpPermissions=IpPermissions)
    security_group.authorize_ingress(IpPermissions=IpPermissions)

    #
    #   EC2 Instances
    #
    shellcodefile=os.path.abspath(initfile)
    shellfile = open(shellcodefile,'r').read()
    pemfile =os.path.abspath(keyfile)
    instances = subnet.create_instances(
        MinCount=number_instances,
        MaxCount=number_instances,
        UserData=shellfile,
        KeyName=pemkey,
        SecurityGroupIds=[security_group.id],
        ImageId=base_aws_image,
        InstanceType='m4.large'
    )

    # tag instances and assign a public ip
    print("Sleep 60 seconds to give instances time to configure...")
    sleep(60)
    for v in instances:
        v.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('node')}])
        address = client.allocate_address()
        client.associate_address(InstanceId=v.instance_id, PublicIp=address['PublicIp'])
        print("ID: {0:<15}\tIP: {1:<15}\tDNS: {2:<15}".format(v.instance_id, address['PublicIp'], v.public_dns_name))

