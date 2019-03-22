#!/usr/bin/env python3
from flask import Flask, request
import json
import re

from .YouTrackHelper import YouTrackHelper

app = Flask(__name__)


def load_settings():
    with open("config.json", 'r') as f:
        data = json.load(f)
    return data


settings = load_settings()
yt = YouTrackHelper(settings["youtrack_instance_name"], settings["youtrack_token"])

old_branch_pattern = re.compile(r"^i(\d+)($|[_-])")
new_branch_pattern = re.compile(r"^(.+-\d+)($|[_-])")


def get_issue_id(branch_name):
    old_match = old_branch_pattern.match(branch_name)
    new_match = new_branch_pattern.match(branch_name)
    if old_match:
        return "VIMC-" + old_match.group(1)
    elif new_match:
        return new_match.group(1)
    else:
        return None


@app.route('/pull-request/', methods=['POST'])
def assign():
    users = settings["users_dict"]
    payload = request.get_json()
    pr = payload["pull_request"]
    url = pr["url"]

    issue_id = get_issue_id(pr["head"]["ref"])

    if issue_id is None:
        return '', 200

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
