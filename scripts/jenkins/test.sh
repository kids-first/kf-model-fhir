#!/bin/bash

# Run model validation and the integration tests

# --- Requires ---
# See scripts/integration_test.sh for requirements

set -eo pipefail

echo "✔ Begin testing ..."

# -- Setup venv and build dependencies --
PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
virtualenv -p python3 venv
. venv/bin/activate
python -m pip install -e .
python -m pip install -r dev-requirements.txt

# -- Run FHIR model validation --
# Build local IG publisher image which self-cleans
docker build -t kidsfirstdrc/fhir-ig-publisher:latest \
             -f scripts/jenkins/Dockerfile .
# Validate FHIR model
fhirutil validate site_root/ig.ini --publisher_opts='-tx n/a' --no_refresh_publisher

# -- Run integration tests --
./scripts/integration_test.sh jenkins

echo "✅ Finished testing!"
