import os
import uuid

import redis
from flask import Flask, Blueprint, request, flash, redirect, url_for, session
from flask_session import Session
from api import response_generator as r
import json
from broker import message_broker as broker

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)

app.secret_key = '|9vpN<gctB6fBvv5MqV5|XMAOE0Qu3'

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False

pool_session = redis.ConnectionPool(host='localhost', port=6379, db=0)
app.config['SESSION_REDIS'] = redis.Redis(connection_pool=pool_session)

pool_transform = redis.ConnectionPool(host='localhost', port=6379, db=1)
red_transform = redis.Redis(connection_pool=pool_transform)

pool_response = redis.ConnectionPool(host='localhost', port=6379, db=2)
red_response = redis.Redis(connection_pool=pool_response)

sess = Session(app)

# Influx
token = "w-OIV1p_HbWFlEjV_8EFqM5lBL97xyIEXM3IWoFHEXdatEXatLn0ir_IMPRM64-7cL2UKe9X48pMiGLfd2N88Q=="
org = "conet"
bucket = "ba_influx"

with InfluxDBClient(url="http://localhost:8086", token=token, org=org) as client:
    delete_api = client.delete_api()
    bucket_api = client.buckets_api()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    read_api = client.query_api()


def uuid_gen():
    if 'uid' not in session:
        session['uid'] = uuid.uuid4()
    return session['uid']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=["GET"])
def index():
    return r.respond({"uid": str(uuid_gen())})


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        log("warning", "[Server, /upload]: No File Part", uuid_gen())
        return r.respond({"success": False, "status": "No File Part"}, 400)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        log("warning", "[Server, /upload]: No Selected File", uuid_gen())
        return r.respond({"success": False, "status": "No Selected File"}, 400)
    if file and allowed_file(file.filename):
        file_content = file.stream.read().decode("utf-8")
        session['file'] = file_content
        log("info", "[Server, /upload]: File Uploaded", uuid_gen())
    else:
        log("warning", "[Server, /upload]: Filetype Not Allowed", uuid_gen())
        return r.respond({"success": False, "status": "Filetype Not Allowed"}, 400)

    return r.respond({"file": session['file']})


@app.route('/transform', methods=['POST'])
def transform_route():
    transform_json = request.json

    if session['file'] != '':
        file = str(session['file'])
        file = file.split(transform_json['seperator'])
        log("info", "[Server, /transform]: File Transformed", uuid_gen())
        red_transform.set(str(uuid_gen()), json.dumps(transform_json))
        return r.respond({"fileParts": file})


def transform(file, transform_json):
    transform_json = json.loads(transform_json.decode("utf-8"))
    messages = file.split(transform_json['seperator'])
    return messages


@app.route('/send', methods=['POST'])
def send():
    service = request.json['service']
    messages = transform(str(session['file']), red_transform.get(str(uuid_gen())))
    for m in messages:
        log("trace", f"[Server, /send]: Send to {service}: {m}", uuid_gen())
        broker.produce(uuid_gen(), service, m)
    return r.respond({"requestSend": True})


@app.route('/receive', methods=['POST'])
def receive():
    log("info", f"[Server, /receive]: Received from {request.json['service']}: {request.json['message']}", uuid_gen())
    if red_response.exists(request.json['uid']):
        saved_response = red_response.get(request.json['uid']).decode('utf-8')
        red_response.set(request.json['uid'], saved_response + "<!-!>" + request.json['message'])
    else:
        red_response.set(request.json['uid'], request.json['message'])
    return r.respond({"successful": True})


@app.route('/poll', methods=['GET'])
def poll():
    if red_response.exists(str(uuid_gen())):
        response = red_response.get(str(uuid_gen())).decode('utf-8')
        log("info", f"[Server, /poll]: Response poll from cache successful", uuid_gen())
        red_response.delete(str(uuid_gen()))
        log("info", f"[Server, /poll]: Deleted cached response", uuid_gen())
        return r.respond({"successful": True, "response": response})
    log("warning", f"[Server, /poll]: No cached responses", uuid_gen())
    return r.respond({"successful": False})


@app.route('/log', methods=['POST'])
def log_route():
    log(request.json['level'], request.json['message'], str(uuid_gen()))
    return r.respond({"successful": True})


def log(level, message, uid):
    point = Point("logs") \
        .tag("uid", str(uid)) \
        .tag("level", level) \
        .field("message", message) \
        .time(datetime.utcnow(), WritePrecision.NS)

    write_api.write(bucket, org, point)


@app.route('/delete', methods=['POST'])
def delete():
    delete_api.delete(start="2010-01-01T00:00:00Z", stop=datetime.now(), bucket=bucket, predicate="")
    return r.respond({"successful": True})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, use_reloader=False)
