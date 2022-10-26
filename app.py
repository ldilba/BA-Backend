import os
import uuid

import redis
from flask import Flask, Blueprint, request, flash, redirect, url_for, session
from flask_session import Session
from api import response_generator as r
import json
from broker import message_broker as broker

ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)

app.secret_key = '|9vpN<gctB6fBvv5MqV5|XMAOE0Qu3'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

sess = Session(app)


def uuid_gen():
    if 'uid' not in session:
        session['uid'] = uuid.uuid4()
    return session['uid']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=["GET"])
def index():
    # session['uid'] = uuid_gen.uuid4()
    return r.respond({"session": str(uuid_gen())})


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return r.respond({"success": False, "status": "No File Part"}, 400)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return r.respond({"success": False, "status": "No Selected File"}, 400)
    if file and allowed_file(file.filename):
        file_content = file.stream.read().decode("utf-8")
        print(file_content)
        session['file'] = file_content
    else:
        return r.respond({"success": False, "status": "Filetype Not Allowed"}, 400)

    return r.respond({"file": session['file']})


@app.route('/transform', methods=['POST'])
def transform():
    transform_json = request.json

    if session['file'] != '':
        file = str(session['file'])
        file = file.split(transform_json['seperator'])
        return r.respond({"fileParts": file})


@app.route('/send', methods=['POST'])
def send():
    message = request.json['message']
    service = request.json['service']
    broker.produce(uuid_gen(), service, message)
    return r.respond({"requestSend": True})


@app.route('/receive', methods=['POST'])
def receive():
    uuid_gen()
    print(request.json)

    return r.respond({"successful": True})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, use_reloader=False)
