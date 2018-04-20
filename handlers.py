import base64
import json
import logging
import os

import boto3
from botocore.client import ClientError
from TwitterAPI import TwitterAPI
from botocore.exceptions import ClientError

import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_tweets(event, context):

    logger.info('Initiate getting tweets')

    twitter_consumer_key = get_parameter(config.TWITTER_CONSUMER_KEY)
    twitter_consumer_secret = get_parameter(config.TWITTER_CONSUMER_SECRET)
    twitter_access_token_key = get_parameter(config.TWITTER_ACCESS_TOKEN)
    twitter_access_token_secret = get_parameter(config.TWITTER_ACCESS_TOKEN_SECRET)

    twitter = TwitterAPI(
        consumer_key=twitter_consumer_key,
        consumer_secret=twitter_consumer_secret,
        access_token_key=twitter_access_token_key,
        access_token_secret=twitter_access_token_secret
    )
    response = twitter.request(
        'statuses/filter', {'locations': '122.87,24.84,153.01,46.84'})

    kinesis = boto3.client(
        'kinesis', region_name=os.environ.get('AWS_DEFAULT_REGION'))
    for item in response.get_iterator():

        if 'text' in item:
            logger.debug('Response item: {}'.format(json.dumps(item)))
            kinesis.put_record(
                StreamName='twitter-stream',
                Data=json.dumps(item),
                PartitionKey=' filter'
            )

        elif 'limit' in item:
            logger.info('Rate limit')
            break

        elif 'disconnect' in item:
            logger.warning('disconnecting because {}'.format(item['disconnect']['reason']))
            break

    logger.info('Complete getting tweets')

def save_tweet_data(event, context):

    logger.info('Initiate saving tweet data')

    dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_DEFAULT_REGION'))
    table = dynamodb.Table(config.TWEET_DATA_TABLE)
    items = []
    for record in event['Records']:
        payload = base64.b64decode((record['kinesis']['data']))
        data = json.loads(payload)

        logger.debug('New data: {}'.format(json.dumps(data)))

        new_item = {
            'id': str(data['id']),
            'timestamp': data['timestamp_ms'],
            'text': data['text']
        }

        items.append(new_item)


    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    except ClientError as e:
        logger.error('AWS Error: {}'.format(e.response['Error']['Code']))

        raise e


def get_parameter(key: str) -> str:

    ssm = boto3.client(
        'ssm', region_name=os.environ.get('AWS_DEFAULT_REGION'))

    try:
        response = ssm.get_parameter(Name=key)

        return response['Parameter']['Value']

    except ClientError as e:
        raise e
