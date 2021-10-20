#!/usr/bin/env python3
from flask import Flask, request
import hmac
import hashlib
import json

from .GitHubAPI import GitHubAPI
from .YouTrackAPI import YouTrackAPI
from .Ticket import Ticket


def load_settings():
    with open("config.json", 'r') as f:
        data = json.load(f)
    with open("config.json", 'w') as f:
        # remove sensitive config from disk after reading it into memory
        f.write("")
    return data


settings = load_settings()

app = Flask(__name__)

api = YouTrackAPI(settings["youtrack_instance_name"],
                    settings["youtrack_token"])


gh_api = GitHubAPI()

@app.route('/pull-request/', methods=['POST'])
def assign():

    payload = request.get_json()
    hash_signature = request.headers["X-Hub-Signature"]

    if not signature_matches(request.data, hash_signature):
        return '', 401

    ticket = Ticket(payload, api, gh_api, settings["users_dict"])

    if not ticket.exists():
        return '', 200

    return ticket.update()


def signature_matches(payload, hash_signature):
    secret = bytes(settings["github_secret"], 'latin1')
    signature = 'sha1=' + hmac.new(secret, payload, hashlib.sha1).hexdigest()
    return hmac.compare_digest(signature, hash_signature)
