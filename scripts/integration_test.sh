#!/bin/bash

# Run the integration tests

# Spin up an integration test server if one is not already running
# Run integration tests in the `tests` dir with pytest

# Usage ./scripts/integration_test.sh [ localhost | jenkins ]

# --- Requires ---
# Python dependencies have already been installed

# - Running on localhost -
# Authorization to access to the kidsfirstdrc/smilecdr:test docker image on
# Dockerhub

# Dockerhub credentials in an .env file or the following environment variables:
# DOCKER_HUB_USERNAME - Dockerhub username
# DOCKER_HUB_PW - Dockerhub password

# - Running on Jenkins -
# Jenkins needs authorization to access to the docker image on AWS ECR

set -eo pipefail
set +x

echo "✔ Begin setup for integration tests ..."

if [[ -f .env ]];
then
    source .env
fi

DOCKER_TEST_IMAGE_TAG="2020.05.PRE-14-test"
FHIR_API=${FHIR_API:-'http://localhost:8000'}
FHIR_USER=${FHIR_USER:-admin}
FHIR_PW=${FHIR_PW:-password}

# -- Login to either Dockerhub or AWS ECR --
EXECUTOR=${1:-"localhost"}
echo "Running on $EXECUTOR, logging into Docker registry"
# Use Dockerhub image if running on localhost
if [[ $EXECUTOR == "localhost" ]]; then
    DOCKER_REPO='kidsfirstdrc/smilecdr'
    docker login -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PW
# Use AWS image if running on Jenkins
else
    DOCKER_REPO='232196027141.dkr.ecr.us-east-1.amazonaws.com/kf-strides-smile-cdr'
    if [[ -n $AWS_PROFILE_NAME ]];
    then
        # Use profile if supplied
        passwd=$(aws --profile="$AWS_PROFILE_NAME" ecr get-login --region us-east-1 | awk '{ print $6 }')
    else
        passwd=$(aws ecr get-login --region us-east-1 | awk '{ print $6 }')
    fi
    docker login -u AWS -p $passwd "$DOCKER_REPO"
fi

# -- Run test server --
DOCKER_IMAGE="$DOCKER_REPO:$DOCKER_TEST_IMAGE_TAG"
DOCKER_CONTAINER='fhir-test-server'
EXISTS=$(docker container ls -q -f name=$DOCKER_CONTAINER)
if [ ! "$EXISTS" ]; then
    echo "Begin deploying test server ..."
    docker run -d --rm --name "$DOCKER_CONTAINER" -p 8000:8000 "$DOCKER_IMAGE"
    # Wait for server to come up
    until docker container logs "$DOCKER_CONTAINER" 2>&1 | grep "up and running"
    do
        echo -n "."
        sleep 2
    done
fi

# -- Run tests --
# NOTE - The search parameter tests fail right now because we must wait until
# the server finishes rebuilding the search indices before testing. However,
# currently there isn't a reliable way to tell when server is finishes
# re-indexing.
echo "Test server deployed, begin execution of integration tests ..."
pytest -x -s --deselect=tests/test_app.py::test_search_params tests

echo "✅ Finished integration tests!"
