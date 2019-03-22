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


@app.route('/pull-request/', methods=['POST'])
def assign():
    users = settings["users_dict"]
    payload = request.get_json()
    pr = payload["pull_request"]
    issue_id = pr["head"]["ref"]
    url = pr["url"]

    if payload["action"] == "review_requested":
        assignee = users[pr["requested_reviewers"][0]["login"]]
        print(assignee)
        yt.update_ticket(issue_id,
                         commands=[yt.set_state("Submitted"), yt.assign(assignee)],
                         comment=url)

    if payload["action"] == "closed" and pr["merged"] is True:
        yt.update_ticket(issue_id,
                         commands=[yt.set_state("Ready to deploy"), yt.assign("Unassigned")],
                         comment=url)

    if payload["action"] == "submitted":
        review = payload["review"]
        if review["state"] != "approved":
            yt.update_ticket(issue_id,
                             commands=[yt.set_state("Reopened"), yt.assign(pr["user"]["login"])],
                             comment=url)

    return '', 200
