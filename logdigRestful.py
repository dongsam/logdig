#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dongsamb'

from flask import Flask
from flask_restful import Resource, Api, reqparse
import time
import setup_AWS
import sys


class LogdigRestful(Resource):
    """RESTful Server for get log from `clickTracker.js` and queing to AWS SQS
    """
    python_version = sys.version_info[0]

    if python_version == 2:
        flask_arg_type = unicode
    elif python_version == 3:
        flask_arg_type = str
    else:
        print('check python version')
        sys.exit()

    aws = setup_AWS.AWS()
    queue = aws.get_sqs_queue()

    log_parser = reqparse.RequestParser()
    log_parser.add_argument('timestamp', type=flask_arg_type, required=True)
    log_parser.add_argument('token', type=flask_arg_type, required=True)
    log_parser.add_argument('user_key', type=flask_arg_type, required=True)
    log_parser.add_argument('current_page', type=flask_arg_type, required=True)
    log_parser.add_argument('link', type=flask_arg_type, required=True)
    log_parser.add_argument('x', type=flask_arg_type, required=True)
    log_parser.add_argument('y', type=flask_arg_type, required=True)
    log_parser.add_argument('spent_milli_sec', type=flask_arg_type, required=True)
    log_parser.add_argument('user_agent', type=flask_arg_type, required=True)
    log_parser.add_argument('load_count', type=flask_arg_type, required=True)

    @staticmethod
    def get():
        """ for checking this server alive in browser

        :return: json type success log
        """
        return {'RESTful Server': 'Success'}

    def post(self):
        """parse post data(log) and send message to AWS SQS

        :return: status and duration millisecond of queueing
        """

        s = "|"
        # s : separator

        args = self.log_parser.parse_args()
        # datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")

        log = args["timestamp"] + s + \
            args["token"] + s + \
            args["user_key"] + s + \
            args["current_page"] + s + \
            args["link"] + s + \
            args["x"] + s + \
            args["y"] + s + \
            args["spent_milli_sec"] + s + \
            args["user_agent"] + s + \
            args["load_count"]

        start_time = time.time()
        response = self.queue.send_message(MessageBody=log)

        # Return the performance information
        duration_millisec = str(time.time() - start_time)

        return {
            'status': 'Succeed to send log.',
            'duration_millisecond': duration_millisec
        }

# start server
if __name__ == '__main__':
    # flask settings
    application = Flask(__name__)
    api = Api(application)
    api.add_resource(LogdigRestful, '/')

    @application.after_request
    def after_request(response):
        """solve CORS issue (http://www.davidadamojr.com/handling-cors-requests-in-flask-restful-apis/)

        :param response: response, after request
        :return: header added response
        """
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    application.debug = True
    application.run(host="0.0.0.0")
