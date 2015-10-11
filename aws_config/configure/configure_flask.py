#!/usr/bin/python3
#
#   Configure Kafka on ec2 instances
#
import boto3, os, sys
sys.path.append("..")
from botocore.exceptions import ClientError as BotoClientError
from time import sleep
from create_clusters import get_tag, keyfile
from config_utils import quiet_wrap

# configuration
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':[get_tag('flask-node')]}]

if __name__=="__main__":
    
    # find all the host nodes
    ec2 = boto3.resource('ec2')
    hosts = []
    private_ips = []
    public_dns = []
    reservations = ec2.instances.filter( Filters = my_instances_filters )
    for instance in reservations:
        print("ID: {0:<15}\tIP: {1:<15}".format(instance.instance_id, instance.public_ip_address))
        hosts.append(instance.public_ip_address)
        private_ips.append(instance.private_ip_address)
        public_dns.append(instance.public_dns_name)

    if len(hosts) != len(private_ips):
        raise(RuntimeError("Host and private ips not consistent!"))

    if len(hosts) == 0:
        raise(RuntimeError("No hosts found."))

    #######################################################################
    #   flask
    #######################################################################
    cmd_str = []
    for h in hosts:
        print("Starting flask configuration...")
        cmd_str.append("(cd ../../src/ && tar -zcvf frontend.tmp.tar.gz frontend)")
        cmd_str.append("(cd ../../src/ && scp -i {0} frontend.tmp.tar.gz ubuntu@{1}:)".format(keyfile, h))
        cmd_str.append("(cd ../../src/ && rm frontend.tmp.tar.gz)")
        cmd_str.append("ssh -i {0} ubuntu@{1} tar xvf frontend.tmp.tar.gz".format(keyfile, h))
        
        # launch webapp
        cmd_str.append("ssh -i {0} ubuntu@{1} \"{2}\"".format(keyfile, h, quiet_wrap("sudo ./frontend/run.py")))

    # execute the remote commands
    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    for a in public_dns:
        print("Straw Frontend:\thttp://{0}:5000".format(a))

