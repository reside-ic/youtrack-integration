## YouTrack - GitHub Integration
This Flask app exposes a single endpoint `/pull-request/` to be used as a GitHub webhook for 
[pull request events](https://developer.github.com/v3/activity/events/types/#pullrequestevent) and 
[pull request review events](https://developer.github.com/v3/activity/events/types/#pullrequestreviewevent)

YouTrack tickets and pull requests are associated by git branch name. Branch names must exactly match YouTrack 
ticket ids. 

Actions taken by the webhook:

1. If the event payload `action` field is `review_requested`:
    1. sets the ticket state to "Submitted"
    1. assigns the ticket to the first listed reviewer on the PR
    1. comments on the ticket with the url of the PR
1. If the event payload `action` field is `closed` and `pull_request[merged]` is true:
    1. sets the ticket state to "Ready to deploy"
    1. unassigns the ticket
1. If the event payload `action` field is `submitted` and `review[state]` is "approved":
    1. sets the ticket state to "Reopened"
    1. assigns the ticket back to the PR owner
    
    
## Configuration
The config requires 3 things:
1. the YouTrack instance name
1. a permanent [YouTrack API access token](https://www.jetbrains.com/help/youtrack/standalone/Manage-Permanent-Token.html)
1. a dictionary from GitHub logins to YouTrack usernames

See the `sample.config.json` file.

## Tests
To run tests :
1. `pip3 install -r requirements-dev.txt --user`
1. `pytest`
