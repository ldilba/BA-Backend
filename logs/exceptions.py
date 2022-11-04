from functools import wraps

from logs import logger
from api import response_generator as r


def exception_handler(msg=""):
    def exception_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.log("error", f"[Server, {msg}]: {str(e)}", "none")
                return r.respond({"success": False, "error": str(e)})
        return decorator
    return exception_decorator
