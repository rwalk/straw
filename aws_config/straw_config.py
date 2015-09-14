#!/usr/bin/python3
import boto3, os

key_file = "/home/ryan/projects/insight/accounts/rwalker.pem"
install_script = "/home/ryan/projects/insight/aws_config/base_image_config.sh"

# instance filters
my_instances_filters = [{ 'Name': 'instance-state-name', 'Values': ['running']}, {'Name':'tag-value', 'Values':['rwalker-node']}]

if __name__=="__main__":
    ec2 = boto3.resource('ec2')
    reservations = ec2.instances.filter( Filters = my_instances_filters )
    for instance in reservations:
        print("ID: {0:<15}\tIP: {1:<15}\tDNS: {2:<15}".format(instance.instance_id, instance.public_ip_address, instance.public_dns_name))
        #os.system("scp -i {0} {1} ubuntu@{2}:".format(key_file, install_script, instance.public_ip_address))
        #os.system("ssh -v -i {0} ubuntu@{1}".format(key_file, instance.public_ip_address))

