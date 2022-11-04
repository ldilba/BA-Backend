import json

from flask import Blueprint, request
from api import response_generator as r
from database.redis_cache import red_upload, red_transform, red_response
from logs.logs import log
from transform.transform import transform
from util.filenames import allowed_file
from util.uid import uuid_gen
from broker import message_broker as broker
from api.token import token_required

routes = Blueprint('routes', __name__)


@routes.route('/upload', methods=['POST'])
@token_required
def upload_file(uid):
    print(uid)
    # check if the post request has the file part
    if 'file' not in request.files:
        log("warning", "[Server, /upload]: No File Part", uid)
        return r.respond({"success": False, "status": "No File Part"}, 400)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        log("warning", "[Server, /upload]: No Selected File", uid)
        return r.respond({"success": False, "status": "No Selected File"}, 400)
    if file and allowed_file(file.filename):
        file_content = file.stream.read().decode("utf-8")
        print(file_content)
        red_upload.set(uid, file_content)
        log("info", "[Server, /upload]: File Uploaded", uid)
    else:
        log("warning", "[Server, /upload]: Filetype Not Allowed", uid)
        return r.respond({"success": False, "status": "Filetype Not Allowed"}, 400)

    return r.respond({"file": red_upload.get(uid).decode('utf-8')})


@routes.route('/transform', methods=['POST'])
@token_required
def transform_route(uid):
    transform_json = request.json

    if red_upload.get(uid) != '':
        file = red_upload.get(uid).decode('utf-8')
        file = file.split(transform_json['seperator'])
        log("info", "[Server, /transform]: File Transformed", uid)
        red_transform.set(uid, json.dumps(transform_json))
        return r.respond({"fileParts": file})


@routes.route('/send', methods=['POST'])
@token_required
def send(uid):
    service = request.json['service']
    messages = transform(red_upload.get(uid).decode('utf-8'), red_transform.get(uid))
    for m in messages:
        log("trace", f"[Server, /send]: Send to {service}: {m}", uid)
        broker.produce(uid, service, m)
    return r.respond({"requestSend": True})


@routes.route('/receive', methods=['POST'])
def receive():
    log("info", f"[Server, /receive]: Received from {request.json['service']}: {request.json['message']}", uuid_gen())
    if red_response.exists(request.json['uid']):
        saved_response = red_response.get(request.json['uid']).decode('utf-8')
        red_response.set(request.json['uid'], saved_response + "<!-!>" + request.json['message'])
    else:
        red_response.set(request.json['uid'], request.json['message'])
    return r.respond({"successful": True})


@routes.route('/poll', methods=['GET'])
@token_required
def poll(uid):
    if red_response.exists(uid):
        response = red_response.get(uid).decode('utf-8')
        response_messages = response.split('<!-!>')
        log("info", f"[Server, /poll]: Response poll from cache successful", uid)
        red_response.delete(uid)
        log("info", f"[Server, /poll]: Deleted cached response", uid)
        return r.respond({"successful": True, "response": response_messages})
    log("warning", f"[Server, /poll]: No cached responses", uid)
    return r.respond({"successful": False})
