import requests
import re

old_branch_pattern = re.compile(r"^i(\d+)($|[_-])")
new_branch_pattern = re.compile(r"^(.+-\d+)($|[_-])")


class YouTrackAPI:
    base_url = "https://{}.myjetbrains.com/youtrack/rest/"

    def __init__(self, instance_name, token):
        self.token = token
        self.base_url = self.base_url.format(instance_name)

    @staticmethod
    def set_state(state):
        return "state {}".format(state)

    @staticmethod
    def assign(assignee):
        return "for {}".format(assignee)

    def update_ticket(self, issue_id, commands, comment=None):
        params = {
            "command": " ".join(commands)
        }
        if comment is not None:
            params["comment"] = comment
        url_fragment = "issue/{}/execute".format(issue_id)
        r = self.post(url_fragment, params)
        return r.status_code == 200, r

    def post(self, url_fragment, body):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "Content-type": "application/x-www-form-urlencoded"
        }
        url = self.base_url + url_fragment
        response = requests.request("post", url, headers=headers, params=body)
        if response.status_code == 401:
            raise Exception("Failed to authorize against YouTrack")
        return response

    @staticmethod
    def get_issue_id(branch_name):
        old_match = old_branch_pattern.match(branch_name)
        new_match = new_branch_pattern.match(branch_name)
        if old_match:
            return "VIMC-" + old_match.group(1)
        elif new_match:
            return new_match.group(1)
        else:
            return None
