from flask import Flask, jsonify, request, Response
from google.appengine.api import urlfetch
import json, os
import config

# Init Flask app
app = Flask(__name__)

responseEnum = {
    "SYSTEM_STATUS": Response(json.dumps({'system_status': 'OK'}), mimetype='application/json'),
    "INVALID_API_KEY": Response(json.dumps({'error': 'INVALID_API_KEY','error_description': 'api_key provided is not valid'}), mimetype='application/json'),
    "NO_API_KEY": Response(json.dumps({'error': 'NO_API_KEY','error_description': 'api_key not provided'}), mimetype='application/json')
}

@app.route('/')
def root():
    return responseEnum["SYSTEM_STATUS"]

@app.route('/wechat-tonyhelen/markers')
def get_markers():
    return jsonify(json.loads(urlfetch.fetch(url='https://wechat-app-tonyhan.firebaseio.com/markers.json',validate_certificate=True).content))

@app.route('/wechat-tonyhelen/restaurant')
def get_restaurant():
    return jsonify(json.loads(urlfetch.fetch(url='https://wechat-app-tonyhan.firebaseio.com/restaurant.json',validate_certificate=True).content))

@app.route('/message/telegram/<target>', methods=['POST'])
def telegramBot(target):
    if "api_key" not in request.json:
        return responseEnum["NO_API_KEY"], 401
    if request.json["api_key"]!=config.api_key:
        return responseEnum["INVALID_API_KEY"], 401
    chatIdMapping = {"me":"507960755","han":"-276270614"}
    requestUrl = config.telegramWebHookURI + "/sendMessage?chat_id=" + chatIdMapping[target] + "&text=" + request.json["message"]
    return jsonify(json.loads(urlfetch.fetch(url=requestUrl,validate_certificate=True).content))

@app.route('/ip', methods=['GET'])
def ip():
    return Response(request.remote_addr, mimetype="text/text")

@app.route('/view/<target>', methods=['GET'])
def view(target):
    if request.remote_addr in ['::1','2601:646:c601:7239:8c20:8c9e:6790:6127']:
        return 'Page Not Found.',404
    else:
        ipInfo = json.loads(urlfetch.fetch(url='https://api.ipdata.co/' + request.remote_addr + '?api-key=' + config.ip_key,validate_certificate=True).content)
        responseText = "Visit:" + target + "%0AIP:" + ipInfo["ip"] + "%0ACity:" + ipInfo["city"] + "%0ACountry:" + ipInfo["emoji_flag"] + ipInfo["country_name"] + "%0AOrganization:" + ipInfo["organisation"]
        requestUrl = config.telegramWebHookURI + "/sendMessage?chat_id=507960755" + "&text=" + responseText
        return jsonify(json.loads(urlfetch.fetch(url=requestUrl,validate_certificate=True).content))

@app.errorhandler(Exception)
def exception_handler(error):
    return "Internal Server Error:"  + repr(error)