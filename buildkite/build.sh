#!/usr/bin/env bash
set -e
HERE=$(dirname $0)
. $HERE/common

NAME=youtrack-integration-webhook
COMMIT_TAG=$ORG/$NAME:$GIT_SHA
BRANCH_TAG=$ORG/$$NAME:$GIT_BRANCH

docker build -t $COMMIT_TAG -t $BRANCH_TAG .
docker push $COMMIT_TAG
docker push $BRANCH_TAG
