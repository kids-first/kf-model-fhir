#!/bin/bash

# Run model validation and the integration tests

# --- Requires ---
# See scripts/integration_test.sh

set -eo pipefail

echo "✔ Begin testing ..."

# Setup venv and build dependencies
PATH=$WORKSPACE/venv/bin:/usr/local/bin:$PATH
virtualenv -p python3 venv
. venv/bin/activate
python -m pip install -e .
python -m pip install -r dev-requirements.txt

# Run FHIR model validation
chmod -R 777 site_root
fhirutil validate site_root/ig.ini --publisher_opts='-tx n/a'
rm -rf site_root

# Run integration tests
# TODOs

echo "✅ Finished testing!"