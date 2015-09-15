#!/usr/bin/python3
#
#   Configure services on the straw/ec2 instances
#

import boto3, os
from botocore.exceptions import ClientError as BotoClientError
from time import sleep

# configuration
keyfile = "/home/ryan/projects/insight/accounts/rwalker.pem"
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':['rwalker-node']}]

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
        raise(ArgumentError("Host and private ips not consistent!"))

    # just a little hacking to inject some settings into the templates
    # TODO: parallelize this to save some boot time
    zooid = 1
    for h in hosts:
        cmd_str = []
        with open("templates/zoo.cfg.tmp", "w") as tmpfile:
            with open("templates/zoo.cfg","r") as f:
                # copy over the template
                for l in f:
                    tmpfile.write(l)

                # append the server settings
                host_strings= ["server.{0}={1}:2888:3888".format(i+1,private_ips[i]) for i in range(len(hosts))]
                for s in host_strings:
                    tmpfile.write(s + "\n")
                cmd_str.append("scp -i {0} {1} ubuntu@{2}:zoo.cfg".format(keyfile, tmpfile.name, h))
                cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv zoo.cfg /etc/zookeeper/conf/zoo.cfg".format(keyfile, h))

                # Assign the zookeeper ids
                cmd_str.append("ssh -i {0} ubuntu@{1} \" echo 'echo {2} > /var/lib/zookeeper/myid' | sudo -s\" ".format(keyfile, h, zooid))
                zooid+=1

        # execute the remote commands
        for cmd in cmd_str:
            print(cmd)
            res=os.system(cmd)
            if res!=0:
                raise(ArgumentError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    # start each zookeeper
    cmd_str = ["ssh -i {0} ubuntu@{1} sudo service zookeeper restart".format(keyfile, h) for h in hosts]
    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(ArgumentError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))        


