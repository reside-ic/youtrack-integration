#!/usr/bin/env python3
from flask import Flask, request
import json

from YouTrackHelper import YouTrackHelper

app = Flask(__name__)


def load_settings():
    with open("config.json", 'r') as f:
        data = json.load(f)
    return data


settings = load_settings()

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=5000)


@app.route('/pull-request/', methods=['POST'])
def assign():
    payload = request.get_json()
    issue_id = payload["pull_request"]["head"]["ref"]
    assignee = payload["pull_request"]["assignee"]
    yt = YouTrackHelper(settings["youtrack_instance_name"], settings["youtrack_token"])
    yt.assign_ticket(issue_id, assignee)
    return '', 200
