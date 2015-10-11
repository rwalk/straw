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
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':[get_tag('kafka-node')]}]

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
    #   ZOOKEEPER
    ####################################################################### 
    # just a little hacking to inject some settings into the templates
    # TODO: parallelize this to save some boot time
    print("Starting zookeeper configuration...")
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
                raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    # start each zookeeper
    cmd_str = ["ssh -i {0} ubuntu@{1} sudo service zookeeper restart".format(keyfile, h) for h in hosts]
    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))        

    #######################################################################
    #   Kafka
    #######################################################################
    print("Starting kafka configuration...")
    broker_id = 0
    kafka_start_script = "templates/kafka-server-start.sh"
    for i,h in enumerate(hosts):
        cmd_str = []
        with open("templates/kafka.server.properties.tmp", "w") as tmpfile:
            with open("templates/kafka.server.properties","r") as f:
                # copy over the template
                for l in f:
                    tmpfile.write(l)

                # advertise host's private IP
                # tmpfile.write("advertised.host.name: {0}\n".format(h))
                
                # add zookeeper info
                host_strings= ["{0}:2181".format(private_ips[i]) for i in range(len(hosts))]
                tmpfile.write("zookeeper.connect={0}\n".format(",".join(host_strings)))
                
                # set broker id
                tmpfile.write("broker.id={0}\n".format(broker_id))
                broker_id+=1
                
                # add commands to queue
                cmd_str.append("scp -i {0} {1} ubuntu@{2}:server.properties".format(keyfile, tmpfile.name, h))
                cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv server.properties /usr/local/kafka/config/server.properties".format(keyfile, h))
                cmd_str.append("scp -i {0} {1} ubuntu@{2}:kafka-server-start.sh".format(keyfile, kafka_start_script, h))
                cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv kafka-server-start.sh /usr/local/kafka/bin/kafka-server-start.sh ".format(keyfile, h))

        # execute the remote commands
        for cmd in cmd_str:
            print(cmd)
            res=os.system(cmd)
            if res!=0:
                raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    # start each kafka
    cmd_str = ["ssh -i {0} ubuntu@{1} \"nohup sudo /usr/local/kafka/bin/kafka-server-start.sh  /usr/local/kafka/config/server.properties < /dev/null > std.out 2> std.err &\"".format(keyfile, h) for h in hosts]

    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))


    # create the documents and queries topics on one of the Kafka nodes
    
    h = hosts[0]
    cmd_str = ["ssh -i {0} ubuntu@{1} /usr/local/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor {2} --partitions {3} --topic documents".format(keyfile, h, 2, 5), "ssh -i {0} ubuntu@{1} /usr/local/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor {2} --partitions {3} --topic queries".format(keyfile, h, 3, 1)]
    
    for cmd in cmd_str:
        print(cmd)
        res=os.system(cmd)
        if res!=0:
            raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))
