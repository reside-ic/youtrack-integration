import requests


class YouTrackHelper:
    base_url = "https://{}.myjetbrains.com/youtrack/rest/"

    def __init__(self, instance_name, token):
        self.token = token
        self.base_url = self.base_url.format(instance_name)

    def assign_ticket(self, issue_id, assignee, pr_url):
        params = {
            "command": "for {} state Submitted".format(assignee),
            "comment": pr_url
        }
        url_fragment = "issue/{}/execute".format(issue_id)
        r = self.post(url_fragment, params)
        print(r.text)
        return r.status_code == 200, r

    def post(self, url_fragment, body):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "Content-type": "application/x-www-form-urlencoded"
        }
        url = self.base_url + url_fragment
        print(url)
        response = requests.request("post", url, headers=headers, params=body)
        if response.status_code == 401:
            raise Exception("Failed to authorize against YouTrack")
        return response
