import json
import re


def transform(file: str, transform_json):
    transform_json = json.loads(transform_json.decode("utf-8"))
    parts = file.split(transform_json['seperator'])
    messages = []
    for m in parts:
        for replacer in transform_json['replace']:
            m = re.sub(replacer['old'].replace("\\\\", "\\"), replacer['new'], m)
        m = m.strip()
        messages.append(m)
    return messages
