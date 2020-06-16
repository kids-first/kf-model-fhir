#!/bin/bash

# Run the integration tests

# Spin up an integration test server if one is not already running
# Run integration tests in the `tests` dir with pytest

# Usage ./scripts/integration_test.sh

# --- Requires ---
# Python dependencies have already been installed

# Authorization to access to the kidsfirstdrc/smilecdr:test docker image on
# Dockerhub

# Dockerhub credentials in an .env file or the following environment variables:
# DOCKER_HUB_USERNAME - Dockerhub username
# DOCKER_HUB_PW - Dockerhub password


set -eo pipefail

echo "✔ Begin integration tests ..."

if [[ -f .env ]];
then
    source .env
fi

DOCKER_IMAGE='kidsfirstdrc/smilecdr:test'
DOCKER_CONTAINER='fhir-test-server'
FHIR_API=${FHIR_API:-'http://localhost:8000'}
FHIR_USER=${FHIR_USER:-admin}
FHIR_PW=${FHIR_PW:-password}

# -- Run test server --
docker login -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PW
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
pytest -x -s --deselect=tests/test_app.py::test_search_params tests

echo "✅ Finished integration tests!"
