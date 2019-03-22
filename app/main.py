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
yt = YouTrackHelper(settings["youtrack_instance_name"], settings["youtrack_token"])
#
# if __name__ == "__main__":
#     # Only for debugging while developing
#     app.run(host='0.0.0.0', debug=True, port=5000)


@app.route('/pull-request/', methods=['POST'])
def assign():
    users = settings["users_dict"]
    payload = request.get_json()
    pr = payload["pull_request"]
    issue_id = pr["head"]["ref"]
    url = pr["url"]

    if payload["action"] is "review_requested":
        assignee = users[pr["requested_reviewers"][0]["login"]]
        yt.assign_ticket(issue_id, assignee, url)
        yt.set_ticket_state(issue_id, "Submitted")

    if payload["action"] is "closed" and pr["merged"] is True:
        yt.assign_ticket(issue_id, "Unassigned", None)
        yt.set_ticket_state(issue_id, "Ready to deploy")

    if payload["action"] is "submitted":
        review = payload["review"]
        if review["state"] is not "approved":
            yt.assign_ticket(issue_id, pr["user"]["login"], review["html_url"])
            yt.set_ticket_state(issue_id, "Reopened")

    return '', 200
