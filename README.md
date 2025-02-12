## YouTrack - GitHub Integration
[![Build status](https://badge.buildkite.com/9079a4a8af7ed89debf5b094a76b2931cb12df49c136caef92.svg?branch=master)](https://buildkite.com/mrc-ide/youtrack-webhook)

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
1. If the event payload `action` field is `submitted` and `review[state]` is not "approved":
    1. sets the ticket state to "Reopened"
    1. assigns the ticket back to the PR owner


## Configuration
See the `config.json` file.
The config requires 4 things:
1. the YouTrack instance name
1. a permanent [YouTrack API access token](https://www.jetbrains.com/help/youtrack/standalone/Manage-Permanent-Token.html)
1. a secret token used by GitHub to secure the webhook: see https://developer.github.com/webhooks/securing/
1. a dictionary from GitHub logins to YouTrack usernames

If a config value is provided in the format "VAULT:path:key" in will be resolved by looking up the secret from vault.

## Deployment
The app runs inside a docker container and is mapped to port 4567 on the host machine. We currently have this deployed on support.montagu.dide.ic.ac.uk (see [montagu-machine](https://github.com/vimc/montagu-machine/blob/master/docs/Support.md)).
To deploy:
1. if already running, remove the container: `docker rm -f youtrack-integration`
1. `pip3 install -r requirements.txt`
1. `./run --use-vault` to first resolve secrets before running the app

## Tests
To run tests :
1. `pip3 install -r requirements-dev.txt --user`
1. `pytest`

## CI
On Buildkite:
1. `./buildkite/test.sh` runs tests in a docker container
1. `./buildkite/build.sh` builds and pushes the docker image

## Adding the webhook

The webhook can be added to a whole organisation or to a repository.  For the `mrc-ide` org it will be most appropriate to only activate individual repositories.

1. Go to `https://github.com/:org/:repo/settings/hooks` or `https://github.com/organizations/:org/settings/hooks`
2. Click `Add Webhook`
3. Payload URL is https://montagu.vaccineimpact.org/pull-request/
4. Content type is `application/json`
5. Secret from the vault as `vault read secret/youtrack-integration/github`
6. Select "Let me select individual events" and select "Pull requests" and "Pull request reviews"
7. Click the big green "Add webhook" button
