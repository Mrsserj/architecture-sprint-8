import os
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from .auth import IAMClient


app = Flask(__name__)
CORS(app)


@app.route("/reports", methods=["GET"])
@cross_origin()
def get_reports():
    bearer = request.headers.get('Authorization')
    token = bearer.split()[1]

    iam_url = os.environ["KEYCLOAK_URL"]
    realm_name = os.environ["KEYCLOAK_REALM"]
    client_id = os.environ["KEYCLOAK_CLIENT_ID"]
    client_secret = os.environ["KEYCLOAK_CLIENT_SECRET"]

    keycloak = IAMClient(iam_url, realm_name, client_id, client_secret)
    status, roles = keycloak.get_roles(token)    

    if status != 0:
        return {}, 401
    elif "prothetic_user" not in roles:
        return {}, 403

    return {"This is": "report!"}, 200