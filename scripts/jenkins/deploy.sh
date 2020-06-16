#!/bin/bash

# Deploy the FHIR model to the server

# --- Environment Vars ---
# FHIR_API  - FHIR server base URL
# FHIR_USER - FHIR server username with write access
# FHIR_PW   - FHIR server password for FHIR_USER

set -eo pipefail

echo "✔ Begin FHIR model deployment ..."
. venv/bin/activate

if [[ -f .env ]];
then
    source .env
fi

FHIR_API=${FHIR_API:-'http://localhost:8000'}
FHIR_USER=${FHIR_USER:-admin}
FHIR_PW=${FHIR_PW:-password}

VERSION=$(cat "site_root/input/ImplementationGuide-KidsFirst.json" | jq .version)
echo "Deploying Kids First FHIR model $VERSION to $FHIR_USER@$FHIR_API"

fhirutil publish site_root/input/resources/terminology \
--base_url="$FHIR_API" --username="$FHIR_USER" --password="$FHIR_PW"

fhirutil publish site_root/input/resources/extensions \
--base_url="$FHIR_API" --username="$FHIR_USER" --password="$FHIR_PW"

fhirutil publish site_root/input/resources/profiles \
--base_url="$FHIR_API" --username="$FHIR_USER" --password="$FHIR_PW"

fhirutil publish site_root/input/resources/search \
--base_url="$FHIR_API" --username="$FHIR_USER" --password="$FHIR_PW"

echo "✅ Finished deploying model!"
