from flask import request


def api_key_auth(header_key, expected_value):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if request.headers.get(header_key) != expected_value:
                return "Unauthorized", 401
            result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator
