import json


def transform(file, transform_json):
    transform_json = json.loads(transform_json.decode("utf-8"))
    messages = file.split(transform_json['seperator'])
    return messages
