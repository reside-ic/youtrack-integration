#!/usr/bin/env python3
from flask import Flask, request
import hmac
import hashlib
import json

from .YouTrackHelper import YouTrackHelper


def load_settings():
    with open("config.json", 'r') as f:
        data = json.load(f)
    with open("config.json", 'w') as f:
        f.write("")  # remove sensitive config from disk after reading it into memory
    return data


settings = load_settings()

app = Flask(__name__)

yt = YouTrackHelper(settings["youtrack_instance_name"], settings["youtrack_token"])


@app.route('/pull-request/', methods=['POST'])
def assign():

    payload = request.get_json()
    hash_signature = request.headers["X-Hub-Signature"]

    if not signature_matches(request.data, hash_signature):
        return '', 401

    pr = payload["pull_request"]
    url = pr["html_url"]

    branch_name = pr["head"]["ref"]
    issue_id = YouTrackHelper.get_issue_id(branch_name)

    if issue_id is None:
        print("No YouTrack issue associated with branch {}".format(branch_name))
        return '', 200

    if payload["action"] == "review_requested":
        return submit(issue_id, pr, url)

    if payload["action"] == "closed" and pr["merged"] is True:
        return close(issue_id, url)

    if payload["action"] == "submitted":
        review = payload["review"]
        if review["state"] != "approved":
            return reopen(issue_id, pr, review)

    return '', 200


def reopen(issue_id, pr, review):
    if pr["user"]["login"] != review["user"]["login"]:  # ignore author reviewing their own code
        users = settings["users_dict"]
        assignee = users[pr["user"]["login"]]
        review_url = review["html_url"]
        print("Reopening ticket {} and assigning user {}".format(issue_id, assignee))
        success, response = yt.update_ticket(issue_id,
                                             commands=[yt.set_state("Reopened"), yt.assign(assignee)],
                                             comment=review_url)
        if not success:
            return response.text, response.status_code
    return '', 200


def close(issue_id, url):
    print(("Closing ticket {} and unassigning".format(issue_id)))
    success, response = yt.update_ticket(issue_id,
                                         commands=[yt.set_state("Ready to deploy"), yt.assign("Unassigned")],
                                         comment=url)
    if not success:
        return response.text, response.status_code
    return '', 200


def submit(issue_id, pr, url):
    users = settings["users_dict"]
    assignee = users[pr["requested_reviewers"][0]["login"]]
    print("Submitting ticket {} and assigning user {}".format(issue_id, assignee))
    success, response = yt.update_ticket(issue_id,
                                         commands=[yt.set_state("Submitted"), yt.assign(assignee)],
                                         comment=url)
    if not success:
        return response.text, response.status_code
    return '', 200


def signature_matches(payload, hash_signature):
    secret = bytes(settings["github_secret"], 'latin1')
    signature = 'sha1=' + hmac.new(secret, payload, hashlib.sha1).hexdigest()
    return hmac.compare_digest(signature, hash_signature)
