#!/usr/bin/env bash

git_id=$(git rev-parse --short=7 HEAD)
git_branch=$(git symbolic-ref --short HEAD)

pip3 install --quiet -r requirements-dev.txt
python3 -m pytest

org=vimc
name=youtrack-integration-webhook

commit_tag=$org/$name:$git_id
branch_tag=$org/$name:$git_branch

docker build -t $commit_tag -t $branch_tag .
docker push $commit_tag
docker push $branch_tag
