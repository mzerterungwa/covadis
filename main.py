# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is a sample for a weather fulfillment webhook for an Dialogflow agent
This is meant to be used with the sample weather agent for Dialogflow, located at
https://console.dialogflow.com/api-client/#/agent//prebuiltAgents/Weather

This sample uses the WWO Weather Forecast API and requires an WWO API key
Get a WWO API key here: https://developer.worldweatheronline.com/api/
"""
from flask_redis import FlaskRedis
from envyaml import EnvYAML
from passlib.hash import pbkdf2_sha256
# read file env.yaml and parse config
env = EnvYAML('env.yaml')
#import the simple HTTP basic auth encoder and decoder.
from basicauth import decode

import os

from rejson import Client, Path

import json

from flask import Flask, request, make_response, jsonify
app = Flask(__name__)
rc = FlaskRedis(app, host=env['redisDB.host'], port=env['redisDB.port'], password=env['redisDB.password'], decode_responses=env['redisDB.DR'])


log = app.logger


@app.route('/', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook

    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    # request.headers is actually an EnvironHeaders object that can be accessed like a dictionary
    # Extract the request headers
    
    headers = dict(request.headers)
    
    
    # To decode an encoded basic auth string:
    
    try:
        encoded_str = headers['Authorization']
        username, password = decode(encoded_str)
        hash = pbkdf2_sha256.hash(password)
        
        #print (username, hash)
        #print(env['project.name'])
        if username != env['config.username'] and pbkdf2_sha256.verify(password, hash):
           res = "You are not allowed to call this API"
           return make_response(jsonify({'fulfillmentText': res}))
        # else:
        #     res = "ACCESS GRANTED"
        #     return make_response(jsonify({'fulfillmentText': res}))
    except AttributeError:
        res = 'illegal operation'
        return make_response(jsonify({'fulfillmentText': res}))
  
    
    res="Undefined"
    req = request.get_json(silent=True, force=True)
    
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        res =  'json error'
        return make_response(jsonify({'fulfillmentText': res}))

    if action == 'register-truck':
        res = registerTruck(req)    
    else:
        log.error('Unexpected action.')

    #print('Action: ' + action)
    #print('Response: ' + res)

    return make_response(jsonify({'fulfillmentText': res}))


def registerTruck(req):
    """Returns a string containing text with a response to the user
    with the weather forecast or a prompt for more information
    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """

    license_plate = req['queryResult']['parameters']['license_plate_number']
    surname = req['queryResult']['parameters']['surname']
    other_names = req['queryResult']['parameters']['other_names']
    truck_type = req['queryResult']['parameters']['truck-type']
    consignment_type = req['queryResult']['parameters']['consignment_type']
    start_date = req['queryResult']['parameters']['start_date']
    originating_depot = req['queryResult']['parameters']['originating_depot']
    destination_depot = req['queryResult']['parameters']['destination_depot']
    phon_number = req['queryResult']['parameters']['phon_number']
    consignment_class = req['queryResult']['parameters']['consignment_class']

    drive_info={"Surname":surname, "Other names":other_names, "Truck type":truck_type, "Consignment type":consignment_type, "Start date":start_date, "Originating depot":originating_depot, "Destination depot":destination_depot, "Phone number":phon_number, "Consignment class":consignment_class}
    t_info = rc.hmset(license_plate, drive_info)
    if t_info:
        return "Profile has been succesfully created for truck with license plate number: "+license_plate

    # parameters = req['queryResult']['parameters']
    # msisdn = req['queryResult']['parameters']['phon_number']

    # license_plate = req['queryResult']['parameters']['license_plate_number']
    # rj.jsonset(license_plate, Path.rootPath(), parameters)
    # print 'Account has been created for {}?'.format(rj.jsonget(license_plate, Path('.msisdn')))

    # originalDetectIntentRequest = req['originalDetectIntentRequest']
    # print('Dialogflow Parameters:')
    # print(json.dumps(parameters, indent=4))
    # print(json.dumps(originalDetectIntentRequest, indent=4))
    # return json.dumps(originalDetectIntentRequest, indent=4)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
