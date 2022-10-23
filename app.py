import os

from flask import Flask, request
from flask_cors import CORS, cross_origin

from handler.check import check_logistic_object
from handler.upload import validate_upload_body, upload_image
from utils import api_key_auth
from config import AppConfig

app = Flask(__name__)
CORS(app)
config = AppConfig(header_key="api-key",
                   header_value="")


@app.route("/upload", methods=["POST"], endpoint='upload')
@api_key_auth(header_key=config.AuthHeaderKey, expected_value=config.AuthHeaderValue)
@validate_upload_body
def upload() -> tuple[str, int]:
    """
    Expect JSON Body format
    {
      "photo": "base64",
      "uri": "ONE Record URI"
    }

    Flow of the handler:
     - store .jpg from base64 payload to /tmp/ directory
     - try to find faces in image
     - if faces were found: blur faces
     - upload to GCS
     - create a 1R referred object with GCS object URL
     - send PATCH request to 1R server with given URI

     TBD: --> check if there is an attribute to say if there were faces detected or not

    :return: tuple[str, int]
    """
    return upload_image(request_body=request.json)


@app.route("/check", methods=["POST"], endpoint='check')
@api_key_auth(header_key=config.AuthHeaderKey, expected_value=config.AuthHeaderValue)
def check() -> tuple[str, int]:
    """
    1. frontend tells srv which One Record URI to inspect
    2. inspect
    3. return one record object with marked findings
    :return: tuple[str, int]
    """

    return check_logistic_object(request_body=request.json)


@app.route("/replace", methods=["POST"])
@api_key_auth(header_key=config.AuthHeaderKey, expected_value=config.AuthHeaderValue)
def update() -> tuple[str, int]:
    """
    1. receive 1R URI + which value should be updated
    2. send PATCH request to 1R srv
    3. forward 1R PATCH response
    :return: tuple[str, int]
    """
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
