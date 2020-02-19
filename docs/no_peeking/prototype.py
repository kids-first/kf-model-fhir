#!/usr/bin/env python

# make a new virtualenv in the no_peeking directory, and then 
# pip install -e ../../
# then create environment variables FHIR_USER and FHIR_PASS (ask Avi or Natasha)

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pformat, pprint
from urllib.parse import urlparse

import sqlalchemy

from kf_model_fhir.client import FhirApiClient
from mappings.individual import yield_individuals


def validate_resource(payload):
    resource_type = payload.get('resourceType')
    # Validate by POSTing to the /foo/$validate endpoint
    endpoint = f"{client.base_url}/{resource_type}/$validate"
    success, result = client.send_request('POST', endpoint, json=payload)
    assert success, f"VALIDATE ERROR:\n{pformat(payload)}\n{'-'*80}\n{pformat(result)}"


def send_resource(payload):
    print(f"Sending {payload['id']}", flush=True)
    resource_type = payload.get('resourceType')
    endpoint = f"{client.base_url}/{resource_type}/{payload['id']}"
    success, result = client.send_request('PUT', endpoint, json=payload)
    return success, result, payload


study_id = "SD_PREASA7S"

FHIR_USER = os.getenv("FHIR_USER")
FHIR_PASS = os.getenv("FHIR_PASS")
BASE_URL = 'http://10.10.1.191:8000'
FHIR_VERSION = '4.0.0'

client = FhirApiClient(base_url=BASE_URL, fhir_version=FHIR_VERSION, auth=(FHIR_USER, FHIR_PASS))


def db_study_url(db_maintenance_url, study_id):
    return urlparse(db_maintenance_url)._replace(path=f"/{study_id}").geturl()


eng = sqlalchemy.create_engine(
    db_study_url(os.getenv("KF_WAREHOUSE_DB_URL"), study_id),
    connect_args={"connect_timeout": 5},
    server_side_cursors=True
)

schema="Ingest:meen_pcgc/GuidedTransformStage"

with ThreadPoolExecutor() as tpex:
    # Individuals
    futures = [
        tpex.submit(send_resource, payload)
        for payload in yield_individuals(eng, f'"{schema}".default', study_id)
    ]
    for f in as_completed(futures):
        success, result, payload = f.result()
        assert success, f"SUBMIT ERROR:\n{pformat(payload)}\n{'-'*80}\n{pformat(result)}"
