from flask import Flask, Blueprint, request
from api import response_generator as r

app = Flask(__name__)


@app.route('/', methods=["GET"])
def index():
    return r.respond({"test": True})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3210, use_reloader=False)
