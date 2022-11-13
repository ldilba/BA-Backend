from datetime import datetime

from flask import Blueprint, request
from api import response_generator as r
from api.token import token_required
from database.db import cnxpool_logs

logs = Blueprint('logs', __name__)


@logs.route('/log', methods=['POST'])
@token_required
def log_route(uid):
    log(request.json['level'], request.json['message'], uid)
    return r.respond({"successful": True})


def log(level, message, uid):
    cnx = cnxpool_logs.get_connection()
    cursor = cnx.cursor()
    query = f"INSERT INTO logs (`level`, `message`, `timestamp`, `uid`) " \
            f"VALUES ('{level}', '{message}', '{datetime.utcnow()}', '{str(uid)}')"
    cursor.execute(query)
    cnx.close()
