import base64
from image_classification import *
import os
from constants import *
from apphelper import *


def image_classification(img_encode,imageName):
    img_encode=bytes(img_encode,'utf-8')
    with open("imageToSave.jpg", "wb") as decoded_img:
        decoded_img.write(base64.decodebytes(img_encode))
    object_name_test = os.path.basename("imageToSave.jpg")
    try:
        upload_file_to_bucket(object_name_test, BUCKET_NAME_INPUT, '{}{}'.format(S3_INPUT_FOLDER,imageName+".jpg"))
    except ClientError as e:
        logging.error(e)
    print('uploaded file to bucket')
    result = classify("imageToSave.jpg")
    os.remove("imageToSave.jpg")
    object_name_test=False
    return(result)

# GET REQUEST & RESPONSE QUEUE URLS
request_queue_url = get_queue(REQUEST_QUEUE_NAME)
response_queue_url = get_queue(RESPONSE_QUEUE_NAME)


#polling for mesages
CURRENT_CTR = 0
while (CURRENT_CTR < CTR_MAX):
    imageid_from_request_queue_url = receive_message(request_queue_url, 1)
    if 'Messages' in imageid_from_request_queue_url:
        message = imageid_from_request_queue_url['Messages'][0]
        body_string = message['Body']
        body = json.loads(body_string)
        image_enc = body['image']
        job_id = body['job_id']
        img_name = body['name']

        image_classification_output = image_classification(image_enc,img_name)
        response_queue_message = '({}, {})'.format(
            "imagereceived", image_classification_output[15:])
        print('result classification was {}'.format(response_queue_message))

        file_to_store = '{}_Result.txt'.format(img_name)
        s3write = open(file_to_store, "w+")
        s3write.write(image_classification_output[15:])
        s3write.close()

        upload_file_to_bucket(file_to_store, BUCKET_NAME_OUTPUT, '{}{}'.format(S3_OUTPUT_FOLDER, file_to_store))
        print('uploaded')
        send_message(response_queue_url, {}, job_id, response_queue_message)

        receipt_handle = message['ReceiptHandle']
        message_delete(request_queue_url, receipt_handle)

        CURRENT_CTR = 0
    else:
        CURRENT_CTR += 1

# terminate instance
instanceid_to_kill = get_instance_id()
terminate_instance(instanceid_to_kill)

