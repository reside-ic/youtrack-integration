#!/usr/bin/env bash
set -e
HERE=$(dirname $0)
. $HERE/common

NAME=youtrack-integration-webhook-test
COMMIT_TAG=$ORG/$NAME:$GIT_SHA

docker build -f buildkite/test.dockerfile .
