from datetime import datetime

from flask import Blueprint, request
from api import response_generator as r
from database.db import cnxpool
from util.uid import uuid_gen

logs = Blueprint('logs', __name__)


@logs.route('/log', methods=['POST'])
def log_route():
    log(request.json['level'], request.json['message'], str(uuid_gen()))
    return r.respond({"successful": True})


def log(level, message, uid):
    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()
    query = f"INSERT INTO logs (`level`, `message`, `timestamp`, `uid`) " \
            f"VALUES ('{level}', '{message}', '{datetime.utcnow()}', '{str(uid)}')"
    cursor.execute(query)
    cnx.close()
