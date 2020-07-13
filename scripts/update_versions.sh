#!/usr/bin/env bash

python3 -m venv venv
source venv/bin/activate
pip install .

fhirutil update-versions "$1"
