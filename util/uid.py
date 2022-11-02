import uuid

from flask import session


def uuid_gen():
    if 'uid' not in session:
        session['uid'] = uuid.uuid4()
    return session['uid']
