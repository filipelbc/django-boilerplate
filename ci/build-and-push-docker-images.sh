#!/bin/bash
#
# Run this from the root of the repo.

set -ex

registry=registry.gitlab.com/filipelbc/django-boilerplate

# Main CI image
docker build -f ci/Dockerfile -t $registry/ci:latest .

# Postgres
docker pull postgres:13
docker tag postgres:13 $registry/postgres:latest

# Upload to Gitlab CI
docker login registry.gitlab.com

docker push $registry/ci:latest
docker push $registry/postgres:latest
