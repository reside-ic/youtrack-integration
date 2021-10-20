import requests


class GitHubAPI:

    @staticmethod
    def get(url):
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.request("get", url, headers=headers)
        if response.status_code == 401:
            raise Exception("Failed to authorize against GitHub")
        return response.json()
