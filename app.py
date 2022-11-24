import threading
import time

from flask import Flask

from api import response_generator as r
from api.token import encode_token
from logs.exceptions import exception_handler
from broker.message_broker import receive

from logs.logger import logs
from routes.routes import routes
from routes.services import services
from util.uid import uuid_gen
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(logs)
app.register_blueprint(services)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=["GET"])
@exception_handler("Index")
def index():
    token = encode_token({'uid': str(uuid_gen())})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


def start_server():
    app.run(host="0.0.0.0", port=80, use_reloader=False)


def start_broker():
    receive()


if __name__ == '__main__':
    thread_server = threading.Thread(target=start_server, daemon=True).start()
    thread_broker = threading.Thread(target=start_broker, daemon=True).start()
    while True:
        time.sleep(1)
