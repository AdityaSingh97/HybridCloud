import boto3
import logging
import socket
from botocore.exceptions import ClientError

ACCESS_ID='AKIAZO5EGW22ZRV7TT4R'
ACCESS_KEY='zvV4/aQ4oAVeZhmvm6jKebi/nb2v5/6u7yVWImlC'
#loading sqs
sqs_resource = boto3.resource('sqs',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)
sqs_client = boto3.client('sqs',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key=ACCESS_KEY)

#loading s3 bucket
s3_client = boto3.client('s3',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key= ACCESS_KEY)
s3_resource = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key= ACCESS_KEY)


ec2_client = boto3.client('ec2',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key= ACCESS_KEY)
ec2_res = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=ACCESS_ID,aws_secret_access_key= ACCESS_KEY)



def get_queue(queue_name):
    return sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']


# send message to queue
def send_message(queue_url, message_attributes, message_group_id, message_body):
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageAttributes=message_attributes,
        MessageGroupId=message_group_id,
        MessageBody=message_body
    )
    return response['MessageId']


def receive_message(queue_url, num_messages):
    return sqs_client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MessageAttributeNames=['All'],
        MaxNumberOfMessages=num_messages,
    )


def message_delete(queue_url, receipt_handle):
    sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )



def upload_file_to_bucket(file_name, bucket_name, object_name):
    if object_name is None:
        object_name = file_name
    # Upload the file
    response = s3_client.upload_file(file_name, bucket_name, object_name)
    print(response)


def get_instance_id():
    hostname = '{}.ec2.internal'.format(socket.gethostname())
    filters = [{'Name': 'private-dns-name', 'Values': [hostname]}]
    response = ec2_client.describe_instances(Filters=filters)["Reservations"]
    return response[0]['Instances'][0]['InstanceId']

def terminate_instance(instance_id):
    ids = []
    ids.append(instance_id)
    ec2_res.instances.filter(InstanceIds=ids).terminate()