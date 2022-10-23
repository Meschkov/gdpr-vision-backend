from flask import request


def validate_upload_body(f):
    def decorator(*args, **kwargs):
        d = request.json
        if d.get("uri", None) is None:
            return {"error": "Missing key 'uri' in requests json body"}, 422

        if d.get("photo", None) is None:
            return {"error": "Missing key 'photo' in requests json body"}, 422

        return f(*args, **kwargs)
    return decorator

