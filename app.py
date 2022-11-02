from flask import Flask
from flask_session import Session

from api import response_generator as r
from database import redis_cache

from logs.logs import logs
from routes.routes import routes
from util.uid import uuid_gen

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(logs)

redis_cache.set_session(app)
sess = Session(app)


@app.route('/', methods=["GET"])
def index():
    return r.respond({"uid": str(uuid_gen())})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, use_reloader=False)
