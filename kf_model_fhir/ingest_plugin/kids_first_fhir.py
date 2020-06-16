"""
This module is translated into an instance of
kf_lib_data_ingest.etl.configuration.target_api_config.TargetAPIConfig which is
used by the Kids First Ingest Library's load stage to populate instances of
target model entities (i.e. participants, diagnoses, etc) with data from the
extracted concepts before those instances are loaded into the target service.

Reference: https://github.com/kids-first/kf-lib-data-ingest

See docstrings in kf_lib_data_ingest.etl.configuration.target_api_config for
more details on the requirements for format and content.
"""
import os
from pprint import pformat

from requests import RequestException

from ncpi_fhir_utility.client import FhirApiClient

from kf_model_fhir.ingest_plugin.resources.kfdrc_patient import Patient

all_targets = [
    Patient,
]

FHIR_USER = os.getenv("FHIR_USER") or 'admin'
FHIR_PW = os.getenv("FHIR_PW") or 'password'
clients = {}


def submit(host, entity_class, body):
    clients[host] = clients.get(host) or FhirApiClient(
        base_url=host, auth=(FHIR_USER, FHIR_PW)
    )

    # drop empty fields
    body = {k: v for k, v in body.items() if v not in (None, [], {})}

    api_path = f"{host}/{body['resourceType']}"
    verb = "POST"
    if "id" in body:
        api_path = f"{api_path}/{body['id']}"
        verb = "PUT"

    success, result = clients[host].send_request(verb, api_path, json=body)

    if success:
        return result["response"]["id"]
    else:
        raise RequestException(
            f"Sent {verb} request to {api_path}:\n{pformat(body)}"
            f"\nGot:\n{pformat(result)}"
        )
