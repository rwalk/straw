#!/usr/bin/python3
#
#   Create the resources for Straw cluster on AWS
#
#   RUN aws configure prior to executing this script.
#
#
import boto3, os, argparse
from botocore.exceptions import ClientError as BotoClientError
from time import sleep

# CONFIG SETTINGS
# TODO: read from file
keyfile = "/home/ryan/projects/insight/accounts/rwalker.pem"
initfile = "base_kafka_image_config.sh"
elasticsearch_initfile = "elasticsearch.sh"
tag_prefix = "rwalker-"
vpc_cidr = "10.0.0.0/27"
subnet_cidr = "10.0.0.0/27"         # we have just one subnet right now
kafka_instances=4                 
elasticsearch_instances=1
base_aws_image = 'ami-5189a661'
pemkey = 'rwalker'

def get_tag(name):
    # all service tags will be prefixed with the "tag_prefix" value
    return (tag_prefix + name)



if __name__=="__main__":

    # argument help
    parser = argparse.ArgumentParser(description='Launch AWS EC2 instances for the straw cluster.')
    parser.add_argument('service', help='Name of service to start. Specify \'all\' to launch all services.')
    args = parser.parse_args()

    # boto3 api: we oddly seem to need both ec2 resource and client
    ec2 = boto3.resource('ec2')
    client= boto3.client('ec2')

    ############################################################
    #
    #   NETWORKING -- common to all services
    #
    ############################################################
    # check if vpc already exists
    vpcid = None
    for v in ec2.vpcs.filter(Filters=[{'Name':'tag-value','Values':[get_tag('vpc')]}]):
        vpcid = v.id
            
    # create the vpc
    if vpcid is None:
        my_vpc = ec2.create_vpc(CidrBlock=vpc_cidr)
        vpc = ec2.Vpc(my_vpc.id)
        vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsSupport={'Value':True})
        vpc.modify_attribute(VpcId=my_vpc.id, EnableDnsHostnames={'Value':True})
        vpc.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('vpc')}])
    else:
        vpc = ec2.Vpc(vpcid)

    #
    # Create a single subnet in vpc
    #
    # subnets
    subnetid = None
    for v in vpc.subnets.filter(Filters=[{'Name':'tag-value','Values':[get_tag('subnet')]}]):
        subnetid = v.id
    if subnetid is None:
        subnet = vpc.create_subnet(CidrBlock=subnet_cidr)
        subnet.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('subnet')}])
    else:
        subnet = ec2.Subnet(subnetid)

    #
    # Create a gateway and attach to vpc
    #
    gatwayid = None
    for v in vpc.internet_gateways.filter(Filters=[{'Name':'tag-value','Values':[get_tag('gateway')]}]):
        gatewayid = v.id
    if gatewayid is None: 
        gateway = ec2.create_internet_gateway()
        gateway.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('gateway')}])
        gateway.attach_to_vpc(VpcId=vpc.id)

    #
    #   Create a route table
    #
    rtid = None        
    for v in vpc.route_tables.filter(Filters=[{'Name':'tag-value','Values':[get_tag('route_table')]}]):
        rtid = v.id
        break
    if rtid is None:
        rt = ec2.create_route_table(VpcId=vpc.id)
        rt.associate_with_subnet(SubnetId=subnet.id)
        rt.create_route(GatewayId=gateway.id, DestinationCidrBlock='0.0.0.0/0')
        rt.create_tags(Tags=[{'Key':'Name', 'Value':get_tag('route_table')}])

    #   
    #   Create a security group -- just one for the vpc right now.
    #
    tag = get_tag('security-group')
    description = 'A security group for kafka clusters.'
    sgid = None
    for v in vpc.security_groups.filter(Filters=[{'Name':'group-name','Values':[tag]}]):
        sgid = v.id
    if sgid is None:
        security_group = ec2.create_security_group(GroupName=tag, Description=description, VpcId=vpc.id)
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
    else:
        security_group = ec2.SecurityGroup(sgid)

    ################################################################
    #
    #   Services
    #
    ################################################################

    if args.service.lower() in ['all','kafka']:
        #########################################
        #   KAFKA CLUSTER
        #########################################
        print("Creating a Kafka cluster...")
        #
        #   EC2 Instances
        #
        shellcodefile=os.path.abspath(initfile)
        shellfile = open(shellcodefile,'r').read()
        pemfile =os.path.abspath(keyfile)
        instances = ec2.create_instances(
            MinCount=kafka_instances,
            MaxCount=kafka_instances,
            UserData=shellfile,
            KeyName=pemkey,
            ImageId=base_aws_image,
            InstanceType='m4.large',
            NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex':0, 'Groups':[security_group.id], 'AssociatePublicIpAddress':True}]
        )

        # tag instances and assign a public ip
        tag='kafka-node'
        print("Sleep 60 seconds to give instances time to configure...")
        sleep(60)
        for v in instances:
            v.create_tags(Tags=[{'Key':'Name', 'Value':get_tag(tag)}])
            # elastic ip assignment 
            #address = client.allocate_address()
            #client.associate_address(InstanceId=v.instance_id, PublicIp=address['PublicIp'])
            print("SERVICE: {0:<15}\tID: {1:<15}\tIP: {2:<15}\tDNS: {3:<15}".format(tag, v.instance_id, v.public_ip_address, v.public_dns_name))

    if args.service.lower() in ['all', 'elasticsearch']:
        #########################################
        #   ELASTICSEARCH CLUSTER
        #########################################

        #   
        #   Create a security group for elasticsearch
        #
        sgid = None
        tag = get_tag('elasticsearch-security-group')
        description = 'A security group for elasticsearch clusters.'
        for v in ec2.security_groups.filter(Filters=[{'Name':'group-name','Values':[tag]}]):
            sgid = v.id
        if sgid is None:
            security_group = ec2.create_security_group(GroupName=tag, Description=description, VpcId=vpc.id)

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
                        }
                    ]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 9200,
                    'ToPort': 9200,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0'
                        }
                    ]
                }
            ]
            security_group.authorize_egress(IpPermissions=IpPermissions)
            security_group.authorize_ingress(IpPermissions=IpPermissions)
        else:
            security_group = ec2.SecurityGroup(sgid)

        #
        #   EC2 Instances
        #
        shellcodefile=os.path.abspath(elasticsearch_initfile)
        shellfile = open(shellcodefile,'r').read()
        pemfile =os.path.abspath(keyfile)
        instances = ec2.create_instances(
            MinCount=elasticsearch_instances,
            MaxCount=elasticsearch_instances,
            UserData=shellfile,
            KeyName=pemkey,
            ImageId=base_aws_image,
            InstanceType='m4.large',
            NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex':0, 'Groups':[security_group.id], 'AssociatePublicIpAddress':True}]
        )

        # tag instances and assign a public ip
        tag='elasticsearch-node'
        print("Sleep 60 seconds to give instances time to configure...")
        sleep(60)
        for v in instances:
            v.create_tags(Tags=[{'Key':'Name', 'Value':get_tag(tag)}])
            print("SERVICE: {0:<15}\tID: {1:<15}\tIP: {2:<15}\tDNS: {3:<15}".format(tag, v.instance_id, v.public_ip_address, v.public_dns_name))
