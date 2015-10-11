#!/usr/bin/python3
#
#   Configure Kafka on ec2 instances
#
import boto3, os, argparse, sys
sys.path.append("..")
from botocore.exceptions import ClientError as BotoClientError
from time import sleep
from create_clusters import get_tag, keyfile
from config_utils import quiet_wrap

# configuration
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':[get_tag('storm-node')]}]

if __name__=="__main__":
    
    # argument help
    parser = argparse.ArgumentParser(description='Configure the storm cluster.')
    parser.add_argument('--elasticsearch', help='Collocate elasticsearch with Storm cluster.', action='store_true')
    args = parser.parse_args()

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
    #   Storm
    #######################################################################
    print("Starting Storm configuration...")
    for h in hosts:
        cmd_str = []
        with open("templates/storm.yaml.tmp", "w") as tmpfile:
            with open("templates/storm.yaml.tmp","r") as f:
                # copy over the template
                for l in f:
                    tmpfile.write(l)

                # add zookeeper info
                tmpfile.write("storm.zookeeper.servers:\n")               
                host_strings= ["    - \"{0}\"\n".format(private_ips[i]) for i in range(len(hosts))]
                for v in host_strings:
                    tmpfile.write(v)

                # declare the master             
                tmpfile.write("nimbus.host: \"{0}\"\n".format(private_ips[0]))
                
                # path to stateful info
                tmpfile.write("storm.local.dir: \"/usr/local/storm/local_state\"\n")

                # supervisor info
                # supervisor.slots.ports:
                #    - 6700
                #    - 6701
                #   etc..
                tmpfile.write("supervisor.slots.ports:\n")
                tmpfile.write("".join(["    -{0}\n".format([6700 + i for i in range(len(hosts))])]))

        # add commands to queue
        cmd_str.append("scp -i {0} {1} ubuntu@{2}:storm.yaml".format(keyfile, tmpfile.name, h))
        cmd_str.append("ssh -i {0} ubuntu@{1} sudo mv storm.yaml /usr/local/storm/conf/storm.yaml".format(keyfile, h))
            
        if h==hosts[0]:
            # start nimbus
            cmd_str.append("ssh -i {0} ubuntu@{1} \"{2}\"".format(keyfile, h, quiet_wrap("sudo /usr/local/storm/bin/storm nimbus")))
            # web ui
            cmd_str.append("ssh -i {0} ubuntu@{1} \"{2}\"".format(keyfile, h, quiet_wrap("sudo /usr/local/storm/bin/storm ui")))
        else:
            cmd_str.append("ssh -i {0} ubuntu@{1} \"{2}\"".format(keyfile, h, quiet_wrap("sudo /usr/local/storm/bin/storm supervisor")))
        
        # execute the remote commands
        for cmd in cmd_str:
            print(cmd)
            res=os.system(cmd)
            if res!=0:
                raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))

    # print some info
    # TODO: retag master and open its 8080 port. 
    print("Master: {0}".format(hosts[0]))
    print("\n".join(["Worker: "+ h for h in hosts[1:]]))    

    if args.elasticsearch == True:
    #######################################################################
    #   Collocated Elasticsearch
    #######################################################################

        cmd_str = []
        for h in hosts:
            cmd_str.append("scp -i {0} {1} ubuntu@{2}:".format(keyfile, "../host_install_scripts/elasticsearch_install.sh", h))
            cmd_str.append("ssh -i {0} ubuntu@{1} sudo ./elasticsearch_install.sh".format(keyfile, h))

        # execute the remote commands
        for cmd in cmd_str:
            print(cmd)
            res=os.system(cmd)
            if res!=0:
                raise(RuntimeError("Something went wrong executing {0}  Got exit: {1}".format(cmd, res)))            
        
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


