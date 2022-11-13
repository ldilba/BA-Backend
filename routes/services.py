import json

from flask import Blueprint, request
from api import response_generator as r
from logs.exceptions import exception_handler
from database.db import cnxpool_services
from logs.logger import log

services = Blueprint('services', __name__)


@services.route('/service', methods=['GET'])
@exception_handler("Services/list")
def service_list():
    cnx = cnxpool_services.get_connection()
    cursor = cnx.cursor()
    query = f"SELECT service, display_name from services"
    cursor.execute(query)
    res = cursor.fetchall()
    services_list = []
    for x in res:
        services_list.append({"service": x[0], "displayName": x[1]})
    cnx.close()
    log("info", f"[Server, /service [GET]]: List {len(services_list)} services", "")
    return r.respond({"services": services_list})


@services.route('/service', methods=['POST'])
@exception_handler("Services/register")
def service_register():
    service = request.json['service']
    display_name = request.json['displayName']
    cnx = cnxpool_services.get_connection()
    cursor = cnx.cursor()
    query = f"INSERT INTO services (`service`, `display_name`) " \
            f"VALUES ('{service}', '{display_name}')"
    cursor.execute(query)
    cnx.close()
    log("info", f"[Server, /service [POST]]: Registered {service}", "")
    return r.respond({"success": True})


@services.route('/service', methods=['DELETE'])
@exception_handler("Services/unregister")
def service_unregister():
    service = request.json['service']
    cnx = cnxpool_services.get_connection()
    cursor = cnx.cursor()
    query = f"DELETE FROM services WHERE `service` = '{service}'"
    cursor.execute(query)
    cnx.close()
    log("info", f"[Server, /service [DELETE]]: Unregistered {service}", "")
    return r.respond({"success": True})
