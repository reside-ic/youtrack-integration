#!/usr/bin/env python3
from flask import Flask, request
import re
import hmac
import hashlib
import json

from .YouTrackHelper import YouTrackHelper


def load_settings():
    with open("config.final.json", 'r') as f:
        data = json.load(f)
    return data


settings = load_settings()

app = Flask(__name__)

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

    payload = request.get_json()
    hash_signature = request.headers["X-Hub-Signature"]

    if not signature_matches(request.data, hash_signature):
        return '', 401

    pr = payload["pull_request"]
    url = pr["html_url"]

    issue_id = get_issue_id(pr["head"]["ref"])

    if issue_id is None:
        return '', 200

    if payload["action"] == "review_requested":
        users = settings["users_dict"]
        assignee = users[pr["requested_reviewers"][0]["login"]]
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


def signature_matches(payload, hash_signature):
    secret = bytes(settings["github_secret"], 'latin1')
    signature = 'sha1=' + hmac.new(secret, payload, hashlib.sha1).hexdigest()
    return hmac.compare_digest(signature, hash_signature)
