# DO NOT CHANGE VALUES FOR THIS FILE
# EVEN OUTSIDE THIS FILE !!!!

REQUEST_QUEUE_NAME = 'requests_sss.fifo'
RESPONSE_QUEUE_NAME = 'response_sss.fifo'

MAX_RETRIES = 12

BUCKET_NAME_INPUT = 'ccp1ip'
BUCKET_NAME_OUTPUT = 'ccp1op'

APP_TIER_PREFIX = 'icarus_app_tier_'

KEY_NAME = 'pass1'

SECURITY_GROUP_ID = 'sg-045b79406ba4dd8b6'

# replace this with custom ami with app tier logic!!
AMI_IMAGE_ID = 'ami-001ff492878c6ac51'

MIN_APP_TIERS = 0
MAX_APP_TIERS = 19

UPLOAD_FOLDER = './uploads/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

S3_OUTPUT_FOLDER = 'OUTPUT/'
S3_INPUT_FOLDER = 'INPUT/'

VISIBLE_MESSAGES = 'ApproximateNumberOfMessages'
INVISIBLE_MESSAGES = 'ApproximateNumberOfMessagesNotVisible'

QUEUE_ATTRIBUTES = {
    'FifoQueue': 'true',
    'ReceiveMessageWaitTimeSeconds': '5',
    'VisibilityTimeout': '30',
    'ContentBasedDeduplication': 'true'
}

USERDATA = '''

'''

INSTANCE_PROFILE = {
    'Arn':'arn:aws:iam::650495047349:instance-profile/Cloudproject1roleec2',
}


