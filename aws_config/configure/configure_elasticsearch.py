#!/usr/bin/python3
#
#   Configure Kafka on ec2 instances
#
import boto3, os, sys
sys.path.append("..")
from botocore.exceptions import ClientError as BotoClientError
from time import sleep
from create_clusters import get_tag

# configuration
keyfile = "/home/ryan/projects/insight/accounts/rwalker.pem"
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':[get_tag('elasticsearch-node')]}]

if __name__=="__main__":
    
    # find all the host nodes
    ec2 = boto3.resource('ec2')
    hosts = []
    private_ips = []
    reservations = ec2.instances.filter( Filters = my_instances_filters )
    for instance in reservations:
        print("ID: {0:<15}\tIP: {1:<15}".format(instance.instance_id, instance.public_ip_address))
        hosts.append(instance.public_ip_address)
        private_ips.append(instance.private_ip_address)

    if len(hosts) != len(private_ips):
        raise(RuntimeError("Host and private ips not consistent!"))

    if len(hosts) == 0:
        raise(RuntimeError("No hosts found."))

    #######################################################################
    #   Elasticsearch
    #######################################################################
    print("Starting elasticsearch configuration...")

    # create a temporary config file
    with open("templates/elasticsearch.yml.tmp", "w") as tmpfile:
        with open("templates/elasticsearch.yml","r") as f:
            # copy over the template
            for l in f:
                tmpfile.write(l)

            # add cloud credentials
            # hack: boto3 doesn't yet offer a way to access the store configuration values
            S = boto3._get_default_session()
            profile = S._session.full_config['profiles']['default']

            # add profile information to elasticsearch config to enable cloud discovery
            tmpfile.write("cloud.aws.access_key: {0}\n".format(profile['aws_access_key_id']))
            tmpfile.write("cloud.aws.secret_key: {0}\n".format(profile['aws_secret_access_key']))
            tmpfile.write("cloud.aws.region: {0}\n".format(profile['region']))
            tmpfile.write("discovery.type: ec2\n")
            tmpfile.write("discovery.ec2.groups: {0}\n".format(get_tag('elasticsearch-security-group')))
            #tmpfile.write("discovery.ec2.host_type: public_ip\n")
            tmpfile.write("cluster.name: {0}\n".format(get_tag('elasticsearch-cluster')))

    # build the command queue
    cmd_str = []               
    for h in hosts:
        # add commands to queue
        cmd_str.append("scp -i {0} {1} ubuntu@{2}:elasticsearch.yml".format(keyfile, tmpfile.name, h))
        cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv elasticsearch.yml /etc/elasticsearch/elasticsearch.yml".format(keyfile, h))

    # start each node
    cmd_str.extend(["ssh -i {0} ubuntu@{1} \"sudo service elasticsearch start\"".format(keyfile, h) for h in hosts])

    # execute the remote commands
    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))
