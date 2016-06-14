#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dongsamb'

import config
from boto3.session import Session
from boto3 import client
import json
import time
import zipfile


class AWS(object):
    """Class for configuration of AWS service.
    """

    # set aws session
    def __init__(self):
        assert config
        self.session = Session(aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                               region_name=config.REGION_NAME)

    def get_sqs_queue(self):
        """Get sqs queue and make if no exist sqs.
        """

        print("[AWS][SQS][get queue]")
        sqs = self.session.resource('sqs')
        try:
            queue = sqs.get_queue_by_name(QueueName=config.sqs_queue_name)
        except Exception as e:
            print("[AWS][SQS][make queue]")
            sqs.create_queue(QueueName=config.sqs_queue_name)
            queue = sqs.get_queue_by_name(QueueName=config.sqs_queue_name)
        assert queue
        return queue

    def get_s3_bucket(self):
        """if no available s3 as name of service , make it.

        :return: object of s3 bucket
        """
        print("[AWS][S3][GET]")
        s3 = self.session.resource('s3')
        # sometimes aws flushing
        for i in range(3):
            try:
                if not s3.Bucket(config.s3_bucket_name) in s3.buckets.all():
                    print("[AWS][S3][make bucket]")
                    s3.create_bucket(Bucket=config.s3_bucket_name,
                                     CreateBucketConfiguration={'LocationConstraint': config.REGION_NAME})
                    print("create bucket success"+config.s3_bucket_name)
                    break
            except Exception as e:
                print("[AWS][S3][make bucket]-fail")
                print(e)
                time.sleep(10)
                # wait flushing aws s3 bucket name

        return s3.Bucket(config.s3_bucket_name)

    def zip_and_upload_to_s3(self, source_file_list, zip_output_path):
        """ zip files in source path list and upload to this boto sessions s3 bucket

        :param source_file_list: list object having paths of each source file [requirement]
        :param zip_output_path: path for output zip file [requirement]
        :return: key of uploaded s3 object
        """
        print("[AWS][S3][upload]")
        s3_bucket = self.session.resource('s3').Bucket(config.s3_bucket_name)
        with zipfile.ZipFile(zip_output_path, 'w') as zip_fp:
            for source_file in source_file_list:
                zip_fp.write(source_file)

        s3_bucket.upload_file(zip_output_path, zip_output_path)
        assert s3_bucket.Object(zip_output_path).key
        return s3_bucket.Object(zip_output_path).key

    def get_lambda_function(self, function_name=config.lambda_function_name,
                            source_file_list=config.lambda_source_file_list,
                            lambda_function_s3key=None):
        """get AWS lambda function and make if no exist in this boto session

        :param function_name: name of lambda function [requirement]
        :param source_file_list: if want upload source files, input list object having paths of each source file
                                [condition][requirement least one with lambda_function_s3key]
        :param lambda_function_s3key: input AWS s3 key of zipfile of lambda sources, if aleady uploaded sources to AWS s3
                                [condition][requirement least one with source_file_list]
        :return:
        """
        aws_lambda_client = client('lambda')

        # If no lambda_function_s3key, upload the zipped lambda
        # codes and get S3 key of uploaded the zip file.
        if not lambda_function_s3key:
            print("[AWS][Lambda][GET]")
            lambda_function_s3key = self.zip_and_upload_to_s3(
                source_file_list=source_file_list,
                zip_output_path=config.SERVICE_NAME+'-aws-lambda-source.zip'
            )
            print(lambda_function_s3key)

        try:
            aws_lambda_function \
                = aws_lambda_client.get_function(FunctionName=function_name)
            assert aws_lambda_function.items()

        except Exception as e:
            print("[AWS][Lambda][make function]")

            # make lambda iam
            aws_iam_client = client('iam')
            basic_role_policy = {
                'Statement': [
                    {
                        'Action': 'sts:AssumeRole',
                        'Effect': 'Allow',
                        'Principal':
                        {
                            'Service': 'lambda.amazonaws.com'
                        }
                    }
                ]
            }

            lambda_role_arn = ""
            try:
                lambda_iam = aws_iam_client.create_role(
                    Path='/',
                    RoleName=function_name+"-lambda-role",
                    AssumeRolePolicyDocument=json.dumps(basic_role_policy)
                )
                assert lambda_role_arn
                lambda_role_arn = lambda_iam['Role']['Arn']

            except Exception as e:
                print("[AWS][Lambda][make IAM Role]")
                lambda_iam = aws_iam_client.get_role(
                    RoleName=function_name+"-lambda-role")
                lambda_role_arn = lambda_iam['Role']['Arn']
                assert lambda_role_arn
            print(lambda_role_arn)

            try:
                response = aws_lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime='python2.7',
                    Role=lambda_role_arn,
                    Handler='lambda_function.lambda_handler',
                    Timeout=60,
                    Code={
                        'S3Bucket': config.s3_bucket_name,
                        'S3Key': lambda_function_s3key
                    }
                )
                assert response

                aws_lambda_function = aws_lambda_client.get_function(
                    FunctionName=function_name)
                assert aws_lambda_function.items()
            except Exception as e:
                print(e)
                # recursive call `get_lambda_function` for solve lambda IAM mappling fail issue temporary
                aws_lambda_function = self.get_lambda_function(
                    function_name, source_file_list, lambda_function_s3key)

        # todo: have to manual scheduled expression settings
        return aws_lambda_function

    def upload_to_eb(self,
                     application_name=config.eb_application_name,
                     source_file_list=config.eb_source_file_list,
                     version_lable_suffix="1"):
        """ Upload Source files to AWS Elastic Beanstalk

        :param application_name: Application name of AWS Elastic Beanstalk, using config.SERVICE_NAME as default value
        :param source_file_list: list object having paths of each source file [requirement]
        :param version_lable_suffix: if aleady uploaded same version, should chnage this lable, default value == 1
        :return:
        """
        eb_source_s3key = self.zip_and_upload_to_s3(
            source_file_list=source_file_list,
            zip_output_path=config.SERVICE_NAME+'-aws-eb-source.zip'
        )
        print(eb_source_s3key)
        version_label = application_name+"-"+version_lable_suffix
        print("[AWS][EB][make Application]")
        eb_client = client('elasticbeanstalk')
        try:
            response = eb_client.create_application(
                ApplicationName=application_name,
                Description=application_name
            )
            assert response
        except Exception as e:
            print("[AWS][EB][aleady exist Application]")
            print(e)

        try:
            print("[AWS][EB][make Application version] "+version_label)
            response = eb_client.create_application_version(
                ApplicationName=application_name,
                VersionLabel=version_label,
                SourceBundle={
                    'S3Bucket': config.s3_bucket_name,
                    'S3Key': eb_source_s3key
                },
                AutoCreateApplication=True,
                Process=False
            )
            assert response
        except Exception as e:
            print(e)

        try:
            print("[AWS][EB][make Application environment] "+version_label)
            response = eb_client.create_environment(
                ApplicationName=application_name,
                EnvironmentName=version_label,
                VersionLabel=version_label,
                SolutionStackName='64bit Amazon Linux 2015.09 v2.0.4 running Python 3.4',
                CNAMEPrefix=version_label
            )
            print(response)
            print("Please wait few minute for launching instance")
            print(version_label+".elasticbeanstalk.com")

        except Exception as e:
            print(
                "[AWS][EB][make Application environment][error or already exist, try update] "+version_label)
            print(e)
            try:
                response = eb_client.update_environment(
                    ApplicationName=application_name,
                    EnvironmentName=version_label,
                    VersionLabel=version_label,
                    SolutionStackName='64bit Amazon Linux 2015.09 v2.0.4 running Python 3.4',
                )
                print(response)
                print("Please wait a few minutes for launching instance")
                print(version_label+".elasticbeanstalk.com")
            except Exception as e:
                print(e)


def main():
    """ `python setup_AWS.py` one line command for setup AWS Infrastructure for this service
    """
    aws = AWS()

    queue = aws.get_sqs_queue()
    assert queue

    s3_bucket = aws.get_s3_bucket()
    assert s3_bucket

    lambda_function = aws.get_lambda_function(source_file_list=config.lambda_source_file_list)
    assert lambda_function

    aws.upload_to_eb(
        source_file_list=config.eb_source_file_list,
        version_lable_suffix=config.eb_version_lable_suffix
    )


if __name__ == '__main__':
    main()
