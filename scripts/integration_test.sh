#!/bin/bash

# Run the integration tests

# Usage ./scripts/integration_test.sh

# --- Environment Variables ---
# AWS_PROFILE_NAME - Use profile to login to ECR if this is set

set -eo pipefail

echo "✔ Begin integration tests ..."

if [[ -f .env ]];
then
    source .env
fi

# TODO - Replace with AWS ECR image
# DOCKER_IMAGE = 538745987955.dkr.ecr.us-east-1.amazonaws.com/kf-smile-cdr:test
DOCKER_IMAGE='kidsfirstdrc/smilecdr:test'
DOCKER_CONTAINER='fhir-test-server'
FHIR_API=${FHIR_API:-'http://localhost:8000'}
FHIR_USER=${FHIR_USER:-admin}
FHIR_PW=${FHIR_PW:-password}

# # Use AWS profile if supplied
# if [[ -n $AWS_PROFILE_NAME ]];
# then
#     passwd=$(aws --profile="$AWS_PROFILE_NAME" ecr get-login --region us-east-1 | awk '{ print $6 }')
# else
#     passwd=$(aws ecr get-login --region us-east-1 | awk '{ print $6 }')
# fi
docker login -u kidsfirstdrc -p $DOCKER_HUB_PW

# -- Run test server --
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
pytest -s tests

echo "✅ Finished integration tests!"
