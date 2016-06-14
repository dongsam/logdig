#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dongsamb'

from flask import Flask
from flask_restful import Api
from logdigRestful import LogdigRestful

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

if __name__ == '__main__':
    # start server
    application.debug = True
    application.run()
