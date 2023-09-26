import socket
import logging
import boto3
from botocore.exceptions import ClientError
from constants import *
# functions for AWS ->

# resource and client ojects for eacg
print('loading sqs')
sqs_res = boto3.resource('sqs')
sqs_client = boto3.client('sqs')

print('loading s3')
s3_client = boto3.client('s3')
s3_res = boto3.resource('s3')

print('loading ec2')
ec2_client = boto3.client('ec2')
ec2_res = boto3.resource('ec2')


# SQS
# create queue (if it doesn't exist)

def create_queue(queue_name, attributes):
    SQS_QUEUE_NAME = queue_name
    # Create a SQS queue
    response = sqs_client.create_queue(
        QueueName=SQS_QUEUE_NAME, Attributes=attributes)
    return response['QueueUrl']


def get_queue_url(queue_name):
    return sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']


def get_one_queue_attribute(queue_url, attribute_name='ApproximateNumberOfMessages'):
    attrs = get_queue_attributes(queue_url)
    if attribute_name in attrs:
        return attrs[attribute_name]
    else:
        return '-'


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


def delete_message(queue_url, receipt_handle):
    sqs_client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )


def create_bucket(bucket_name, region=None):
    try:
        if region is None:
            s3_client.create_bucket(Bucket=bucket_name)
            print("bucket created", bucket_name)
        else:
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def get_instance_id():
    hostname = '{}.ec2.internal'.format(socket.gethostname())
    filters = [{'Name': 'private-dns-name', 'Values': [hostname]}]
    response = ec2_client.describe_instances(Filters=filters)["Reservations"]
    return response[0]['Instances'][0]['InstanceId']



def create_instance(key_name, sec_group_ids, image_id='ami-001ff492878c6ac51', instance_type='t2.micro', min_count=1, max_count=1):

    instancelist = ec2_res.create_instances(
        ImageId='ami-001ff492878c6ac51',
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sec_group_ids],
        UserData=USERDATA,
        IamInstanceProfile=INSTANCE_PROFILE
    )

    for i in range(max_count):
        j = i+1
        instance_id = instancelist[i].instance_id
        print(instance_id)
        ec2_res.create_tags(Resources=[instance_id], Tags=[
            {
                'Key': 'Name',
                'Value': '{}{}'.format(APP_TIER_PREFIX, j),
            },
        ])
    #for status in ec2_res.meta.client.describe_instance_status()['InstanceStatuses']:
    #    print(status)
    #ec2_res.update_instance_state(instance_id,1)


def terminate_instance(instance_id):
    ids = []
    ids.append(instance_id)
    ec2_res.instances.filter(InstanceIds=ids).terminate()


