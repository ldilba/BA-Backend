import json

from flask import Blueprint, request, session
from api import response_generator as r
from database.redis_cache import red_transform, red_response
from logs.logs import log
from transform.transform import transform
from util.filenames import allowed_file
from util.uid import uuid_gen
from broker import message_broker as broker

routes = Blueprint('routes', __name__)


@routes.route('/upload', methods=['POST'])
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


@routes.route('/transform', methods=['POST'])
def transform_route():
    transform_json = request.json

    if session['file'] != '':
        file = str(session['file'])
        file = file.split(transform_json['seperator'])
        log("info", "[Server, /transform]: File Transformed", uuid_gen())
        red_transform.set(str(uuid_gen()), json.dumps(transform_json))
        return r.respond({"fileParts": file})


@routes.route('/send', methods=['POST'])
def send():
    service = request.json['service']
    messages = transform(str(session['file']), red_transform.get(str(uuid_gen())))
    for m in messages:
        log("trace", f"[Server, /send]: Send to {service}: {m}", uuid_gen())
        broker.produce(uuid_gen(), service, m)
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
def poll():
    if red_response.exists(str(uuid_gen())):
        response = red_response.get(str(uuid_gen())).decode('utf-8')
        response_messages = response.split('<!-!>')
        log("info", f"[Server, /poll]: Response poll from cache successful", uuid_gen())
        red_response.delete(str(uuid_gen()))
        log("info", f"[Server, /poll]: Deleted cached response", uuid_gen())
        return r.respond({"successful": True, "response": response_messages})
    log("warning", f"[Server, /poll]: No cached responses", uuid_gen())
    return r.respond({"successful": False})
