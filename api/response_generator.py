import json

from flask import Response


def respond(r, status=200, json_dump=True):
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate, public, max-age=0",
               "Pragma": "no-cache",
               "Expires": "0",
               "Access-Control-Allow-Origin": "*"}
    if json_dump:
        return Response(json.dumps(r), status=status, mimetype='application/json', headers=headers)
    return Response(r, status=status, mimetype='application/json', headers=headers)
