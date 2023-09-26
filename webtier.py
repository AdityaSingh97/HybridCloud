from contextlib import nullcontext
from crypt import methods
from fileinput import filename
import uuid
import os
from flask import Flask, request
from threading import Thread
from threading import Thread
from constants import *
from helper import *
import boto3
import json
import time
import base64
import requests

def process_image(request_queue_url, b64_string, filename, job_id):
    message_attr = {}
    body_object = {
        'image': b64_string,
        'name': filename,
        'job_id': job_id
    }
    body = json.dumps(body_object)
    send_message(request_queue_url, message_attr, job_id, body)

    
def autoscale(url):
    #get length of queue with url given, which denotes the number of req on the SQS
    queue_approx_num_msgs=get_one_queue_attribute(request_queue_url)
    
    #convert to integer
    queue_len=int(queue_approx_num_msgs)
    #get number of running ec2 instances
    num_running_instances=get_running_instances()
    print("no. of running instances {}", num_running_instances)
        
    #launch 19-number of running instances
    max_ec2_launch=MAX_APP_TIERS-num_running_instances
    #take the minimum of number of requests and value calculated above
    num_ec2_launch=min(queue_len,max_ec2_launch)


    ec2 = boto3.resource('ec2')
    # create filter for instances in running state
    filters = [
        {
            'Name': 'instance-state-name', 
            'Values': ['running']
        }
    ]
    
    # filter the instances based on filters() above
    instances = ec2.instances.filter(Filters=filters)

    # instantiate empty array
    RunningInstances = []

    for instance in instances:
        # for each instance, append to array and print instance id
        RunningInstances.append(instance.id)
       # print instance.id
    i_len= len(RunningInstances)
    #create as many instances as calculated
    if(i_len <= 5):    
        create_instance(KEY_NAME,SECURITY_GROUP_ID,'ami-001ff492878c6ac51','t2.micro',1,1)


def get_running_instances():
    instances_run=ec2_res.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['running']}])
    instance_ids=[]
    for instance in instance_ids:
        instance_ids.append(instance)
    return len(instance_ids)

def listen_for_results(response_queue_irl, job_id, job_dictionary):
    res_rec = 0
    j_length = len(job_dictionary)
    while res_rec != j_length:
        resp = receive_message(response_queue_irl, 1)
        print(resp)
        if 'Messages' in resp:
            message = resp['Messages'][0]
            #print(message)
            result = message['Body']
            result=result.replace('(',"")
            result=result.replace(')',"")
            answer = result.split(',')[1]
            #print(result)
            print(answer)
            #body = json.loads(result)
            #print("hello")
            #print(body[2])
            #res_rec += 1
            #response = {
            #    'result': result,
            #    'total': j_length
            #}
            receipt_handle = message['ReceiptHandle']
            delete_message(response_queue_irl, receipt_handle)

def setup_aws_resources():
    create_bucket(BUCKET_NAME_INPUT)
    create_bucket(BUCKET_NAME_OUTPUT)

    request_queue_url = create_queue(REQUEST_QUEUE_NAME, QUEUE_ATTRIBUTES)

    response_queue_url = create_queue(RESPONSE_QUEUE_NAME, QUEUE_ATTRIBUTES)

    return request_queue_url, response_queue_url

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#defining some required variables
request_queue_url = ''
response_queue_url = ''
images = []
jobs= {}
is_get = True

app= Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home_page():
    is_get = (request.method == 'GET')
    job_id = str(uuid.uuid4())

    images = []
    if not is_get:
        file = request.files['myfile']
        print("checking before allowed filename")
        if file and allowed_file(file.filename):
            filename = file.filename
            b64_string = base64.b64encode(file.read())
            #print(b64_string)
            b64_string=b64_string.decode('utf-8')
            images.append(file)
            print("file uploaded", filename)
        process_image(request_queue_url, b64_string,filename, job_id)
        jobs[job_id] = len(images)
        #print("images", images)
        autoscale(request_queue_url)
        #need to set new threads and listen for results
        #spawn = Thread(target=autoscale, args =(request_queue_url,))
        #spawn.start()

        listen = Thread(target=listen_for_results, args=(response_queue_url,job_id,jobs))
        listen.start()


    return "done"

request_queue_url,response_queue_url = setup_aws_resources()
print(request_queue_url)
print(response_queue_url)

if __name__ == '__main__':
    print("listening")
    socket.run(
        app,
        host = "0.0.0.0",
        port=5000
    )

