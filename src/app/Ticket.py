

class Ticket:
    def __init__(self, payload, yt_api, gh_api, users_dict):
        self.payload = payload
        self.action = payload["action"]
        self.yt_api = yt_api
        self.gh_api = gh_api
        self.users_dict = users_dict
        self.pr = payload["pull_request"]
        self.url = self.pr["html_url"]
        self.branch_name = self.pr["head"]["ref"]
        self.issue_id = yt_api.get_issue_id(self.branch_name)

    def exists(self):
        if self.issue_id is None:
            print("No YouTrack issue associated with branch {}".format(
                self.branch_name))
            return False
        return True

    def update(self):
        if self.action == "review_requested":
            reviewer = self.pr["requested_reviewers"][0]["login"]
            return self.__submit(reviewer)

        if self.action == "closed":
            return self.__close()

        if self.action == "submitted":
            review = self.payload["review"]
            author = self.pr["user"]["login"]
            if review["state"] == "approved":
                url = self.pr["url"] + "/reviews"
                reviewer = self.payload["review"]["user"]["login"]
                payload = self.gh_api.get(url)
                remaining_reviews = \
                    [p for p in payload if p["state"] != "APPROVED"
                     and not has_approved(payload, p["user"]["login"])
                     and p["user"]["login"] != reviewer
                     and p["user"]["login"] != author]

                if len(remaining_reviews) > 0:
                    next_reviewer = remaining_reviews[0]["user"]["login"]
                    return self.__submit(next_reviewer)
                return '', 200
            author = self.pr["user"]["login"]
            if author == review["user"]["login"]:
                # ignore author reviewing their own code
                return '', 200
            return self.__reopen(author, review)

        return '', 200

    def __reopen(self, author, review):
        assignee = self.users_dict[author]
        review_url = review["html_url"]
        print("Reopening ticket {} and assigning user {}".format(self.issue_id,
                                                                 assignee))
        commands = [self.yt_api.set_state("Reopened"),
                    self.yt_api.assign(assignee)]
        print(review_url, self.issue_id, commands)
        success, response = self.yt_api.update_ticket(self.issue_id,
                                                      commands=commands,
                                                      comment=review_url)
        if not success:
            return response.text, response.status_code
        return '', 200

    def __close(self):
        if self.pr["merged"] is False:
            return '', 200
        print(("Closing ticket {} and unassigning".format(self.issue_id)))
        commands = [self.yt_api.set_state("Ready to deploy"),
                    self.yt_api.assign("Unassigned")]
        success, response = self.yt_api.update_ticket(self.issue_id,
                                                      commands=commands)
        if not success:
            return response.text, response.status_code
        return '', 200

    def __submit(self, reviewer):
        assignee = self.users_dict[reviewer]
        print(
            "Submitting ticket {} and assigning user {}".format(self.issue_id,
                                                                assignee))
        commands = [self.yt_api.set_state("Submitted"),
                    self.yt_api.assign(assignee)]
        success, response = self.yt_api.update_ticket(self.issue_id,
                                                      commands=commands,
                                                      comment=self.url)
        if not success:
            return response.text, response.status_code
        return '', 200


def has_approved(payload, username):
    return len([p for p in payload if
     p["state"] == "APPROVED" and p["user"]["login"] == username]) > 0
