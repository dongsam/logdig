#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dongsamb'
import datetime
import hashlib
import time
import setup_AWS


def lambda_handler(event, context):
    """ lambda_hadler is default main function name for AWS lambda

    :param event: default param for AWS lambda service
    :param context: default param for AWS lambda service
    :return: json format data, for check status, messages, spent_time in AWS lambda dashboard
    """
    messages_period = 100
    start_time = time.time()

    # if no available sqs queue as name of service , make it
    aws = setup_AWS.AWS()
    queue = aws.get_sqs_queue()

    number_of_messages = int(queue.attributes["ApproximateNumberOfMessages"])

    if number_of_messages < messages_period:
        spent_time = time.time() - start_time
        return_value = {
            'status': 'not running',
            'messages': 'number_of_messages < 100',
            'spent_time': spent_time
        }
        print(return_value)
        return return_value

    past_number_of_messages = number_of_messages

    list_of_messages = []
    logs_s3_body = ""

    print(number_of_messages)
    while number_of_messages:
        messages = queue.receive_messages(MaxNumberOfMessages=10)
        for message in messages:
            logs_s3_body += message.body+"\n"
            list_of_messages.append(message)
            number_of_messages -= 1

    logs_s3_hash = hashlib.sha256(logs_s3_body).hexdigest()

    print(logs_s3_body)
    print(logs_s3_hash)

    today_date = str(datetime.date.today())
    # need to check GMT 0:0 and sync amazon server

    # if no available s3  as name of service , make it
    s3_bucket = aws.get_s3_bucket()

    try:
        res = s3_bucket.put_object(Key=today_date+"/"+logs_s3_hash, Body=logs_s3_body)
        print(res)
    except Exception as e:
        spent_time = time.time() - start_time
        return_value = {
            'status': 'error',
            'messages': e,
            'spent_time': spent_time
        }
        print(return_value)
        return return_value

    # need to res check
    delete_cnt = 0
    for message in list_of_messages:
        message.delete()
        delete_cnt += 1

    if past_number_of_messages == delete_cnt:
        spent_time = time.time() - start_time
        return_value = {
            'status': 'success',
            'messages': 'successful upload log to s3',
            'spent_time': spent_time
        }
        print(return_value)
        return return_value
