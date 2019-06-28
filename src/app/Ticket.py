class Ticket:
    def __init__(self, payload, api):
        self.payload = payload
        self.api = api
        self.pr = payload["pull_request"]
        self.url = self.pr["html_url"]
        self.branch_name = self.pr["head"]["ref"]
        self.issue_id = api.get_issue_id(self.branch_name)

    def exists(self):
        if self.issue_id is None:
            print("No YouTrack issue associated with branch {}".format(
                self.branch_name))
            return False
        return True

    def update(self, users):
        review = self.payload["review"]
        if review["state"] == "approved":
            return '', 200
        author = self.pr["user"]["login"]
        if author == review["user"]["login"]:
            # ignore author reviewing their own code
            return '', 200

        assignee = users[author]
        review_url = review["html_url"]
        print("Reopening ticket {} and assigning user {}".format(self.issue_id,
                                                                 assignee))
        commands = [self.api.set_state("Reopened"), self.api.assign(assignee)]
        print(review_url, self.issue_id, commands)
        success, response = self.api.update_ticket(self.issue_id,
                                                   commands=commands,
                                                   comment=review_url)
        if not success:
            return response.text, response.status_code
        return '', 200

    def close(self):
        if self.pr["merged"] is False:
            return '', 200
        print(("Closing ticket {} and unassigning".format(self.issue_id)))
        commands = [self.api.set_state("Ready to deploy"),
                    self.api.assign("Unassigned")]
        success, response = self.api.update_ticket(self.issue_id,
                                                   commands=commands)
        if not success:
            return response.text, response.status_code
        return '', 200

    def submit(self, users):
        reviewer = self.pr["requested_reviewers"][0]["login"]
        assignee = users[reviewer]
        print(
            "Submitting ticket {} and assigning user {}".format(self.issue_id,
                                                                assignee))
        commands = [self.api.set_state("Submitted"), self.api.assign(assignee)]
        success, response = self.api.update_ticket(self.issue_id,
                                                   commands=commands,
                                                   comment=self.url)
        if not success:
            return response.text, response.status_code
        return '', 200
