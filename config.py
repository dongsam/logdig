#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dongsamb'

# target_service
SERVICE_NAME = 'test-service'  # only lower case characters, number, - and maximum length is 17

# AWS
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
REGION_NAME = 'ap-northeast-1'  # if Tokyo, 'ap-northeast-1'

_sqs_suffix = "-sqs"
_s3_suffix = "-s3"
_lambda_suffix = "-lambda"
_ec2_suffix = "-ec2"
_eb_suffix = "-eb"

sqs_queue_name = SERVICE_NAME+_sqs_suffix
s3_bucket_name = SERVICE_NAME+_s3_suffix
lambda_function_name = SERVICE_NAME+_lambda_suffix
ec2_instance_name = SERVICE_NAME+_ec2_suffix
eb_application_name = SERVICE_NAME+_eb_suffix
eb_version_lable_suffix = "1"  # add when you eb source files and want update eb
# restful_server_url == SERVICE_NAME+eb_version_lable_suffix+".elasticbeanstalk.com"

lambda_source_file_list = ['lambda_function.py', 'config.py', "setup_AWS.py"]
eb_source_file_list = ['application.py', 'logdigRestful.py', 'config.py', "setup_AWS.py", "requirements.txt"]