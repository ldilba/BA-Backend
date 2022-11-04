from flask import Flask

from api import response_generator as r
from api.token import encode_token

from logs.logs import logs
from routes.routes import routes
from util.uid import uuid_gen

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(logs)


@app.route('/', methods=["GET"])
def index():
    token = encode_token({'uid': str(uuid_gen())})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, use_reloader=False)
