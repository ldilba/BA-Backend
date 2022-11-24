import json

from flask import Blueprint, request
from api import response_generator as r
from database.redis_cache import red_upload, red_transform, red_response
from logs.exceptions import exception_handler
from logs.logger import log
from transform.transform import transform
from util.filenames import allowed_file
from util.uid import uuid_gen
from broker import message_broker as broker
from api.token import token_required

routes = Blueprint('routes', __name__)


@routes.route('/upload/file', methods=['POST'])
@exception_handler("Upload file")
@token_required
def upload_file(uid):
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

    return r.respond({"success": True, "content": red_upload.get(uid).decode('utf-8')})


@routes.route('/upload/text', methods=['POST'])
@exception_handler("Upload Text")
@token_required
def upload_text(uid):
    body = request.json
    red_upload.set(uid, body['text'])
    return r.respond({"success": True, "content": body['text']})


@routes.route('/transform', methods=['POST'])
@exception_handler("Transform")
@token_required
def transform_route(uid):
    transform_json = request.json

    if red_upload.get(uid) != '':
        red_transform.set(uid, json.dumps(transform_json))
        log("info", "[Server, /transform]: Transformation saved", uid)
        messages = transform(red_upload.get(uid).decode('utf-8'), red_transform.get(uid))
        log("info", "[Server, /transform]: Messages successfully transformed", uid)
        return r.respond({"success": True, "messages": messages})


@routes.route('/send', methods=['POST'])
@exception_handler("Send")
@token_required
def send(uid):
    service = request.json['service']
    params = request.json['params']

    messages = transform(red_upload.get(uid).decode('utf-8'), red_transform.get(uid))
    expected_responses = len(messages)

    for p in params:
        if "search_size" in p.values():
            expected_responses *= int(p["value"])

    for m in messages:
        log("trace", f"[Server, /send]: Send to {service}: {m}", uid)
        broker.produce(uid, service, m, params)
    return r.respond({"success": True, "messages": expected_responses})


@exception_handler("Receive")
def receive(message):
    log("info", f"[Server, /receive]: Received answer from {message['service']}", uuid_gen())
    if red_response.exists(message['uid']):
        saved_response = red_response.get(message['uid']).decode('utf-8')
        red_response.set(message['uid'], saved_response + "<!-!>" + json.dumps(message['message']))
    else:
        red_response.set(message['uid'], json.dumps(message['message']))

    return r.respond({"successful": True})


@routes.route('/poll', methods=['GET'])
@exception_handler("Poll")
@token_required
def poll(uid):
    if red_response.exists(uid):
        response = red_response.get(uid).decode('utf-8')
        response_messages = response.split('<!-!>')

        for i in range(len(response_messages)):
            response_messages[i] = json.loads(response_messages[i])

        log("info", f"[Server, /poll]: Response poll from cache successful", uid)
        red_response.delete(uid)
        log("info", f"[Server, /poll]: Deleted cached response", uid)
        return r.respond({"successful": True, "response": response_messages})
    log("warning", f"[Server, /poll]: No cached responses", uid)
    return r.respond({"successful": False})
