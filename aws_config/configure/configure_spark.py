#!/usr/bin/python3
#
#   Configure Kafka on ec2 instances
#

import boto3, os, sys
from botocore.exceptions import ClientError as BotoClientError
from time import sleep
sys.path.append("..")
from create_clusters import get_tag, keyfile

# configuration
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':[get_tag('spark-node')]}]

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
    
    # Identify master node
    master = hosts[0]
    #######################################################################
    # Spark requires passwordless SSH
    #######################################################################    
    cmd_str = []
    
    # generate a key on the master
    cmd_str.append("ssh -i {0} ubuntu@{1} \"sudo apt-get -y install ssh rsync && ssh-keygen -f ~/.ssh/id_rsa -t rsa -P \'\' \"".format(keyfile, hosts[0]))

    # download public key temporarily
    cmd_str.append("scp -i {0} ubuntu@{1}:.ssh/id_rsa.pub {2}".format(keyfile, master, "templates/key.tmp"))

    # auth public key for all hosts
    for h in hosts:
        cmd_str.append("scp -i {0} {1} ubuntu@{2}:".format(keyfile, "templates/key.tmp", h))
        cmd_str.append("ssh -i {0} ubuntu@{1} \"cat key.tmp >> ~/.ssh/authorized_keys\"".format(keyfile, h))

    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    #######################################################################
    #   Spark
    #######################################################################
    print("Starting Spark configuration...")
    for i,h in enumerate(hosts):
        cmd_str = []
        with open("templates/spark-env.sh.tmp", "w") as tmpfile:
            with open("templates/spark-env.sh","r") as f:
                # copy over the template
                for l in f:
                    tmpfile.write(l)

                # advertise host's private IP
                tmpfile.write("export SPARK_PUBLIC_DNS={0}\n".format(private_ips[i]))
                                
                # add commands to queue
                cmd_str.append("scp -i {0} {1} ubuntu@{2}:".format(keyfile, tmpfile.name, h))
                cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv spark-env.sh.tmp /usr/local/spark/conf/spark-env.sh".format(keyfile, h))
               
        # execute the remote commands
        for cmd in cmd_str:
            print(cmd)
            res=os.system(cmd)
            if res!=0:
                raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    # send the slaves file to the master
    with open("templates/slaves.tmp", "w") as tmpfile:
        for i,h in enumerate(hosts[1:]):
            tmpfile.write("{0}\n".format(private_ips[i]))

    # add commands to queue
    cmd_str.append("scp -i {0} {1} ubuntu@{2}:".format(keyfile, tmpfile.name, master))
    cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv slaves.tmp /usr/local/spark/conf/slaves".format(keyfile, master))

    # start spark on the master
    cmd_str.append("ssh -i {0} ubuntu@{1} /usr/local/spark/sbin/start-all.sh".format(keyfile, master))

    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    
    
