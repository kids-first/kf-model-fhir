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

from kf_model_fhir.ingest_plugin.target_api_builders.practitioner import (
    Practitioner,
)
from kf_model_fhir.ingest_plugin.target_api_builders.organization import (
    Organization,
)
from kf_model_fhir.ingest_plugin.target_api_builders.practitioner_role import (
    PractitionerRole,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.target_api_builders.family import Family
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_research_study import (
    ResearchStudy,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient_relations import (
    PatientRelation,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_family_relationship import (
    FamilyRelationship,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_condition import (
    Condition,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_phenotype import (
    Phenotype,
)

# from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_vital_status import (
#     VitalStatus,
# )
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_specimen import (
    Specimen,
)

all_targets = [
    Practitioner,
    Organization,
    PractitionerRole,
    Patient,
    Family,
    ResearchStudy,
    PatientRelation,
    FamilyRelationship,
    Condition,
    Phenotype,
    # VitalStatus
    Specimen,
]

FHIR_USER = os.getenv("FHIR_USER") or "admin"
FHIR_PW = os.getenv("FHIR_PW") or "password"
clients = {}


def submit(host, entity_class, body):
    clients[host] = clients.get(host) or FhirApiClient(
        base_url=host, auth=(FHIR_USER, FHIR_PW)
    )

    # drop empty fields
    body = {k: v for k, v in body.items() if v not in (None, [], {})}

    verb = "POST"
    api_path = f"{host}/{entity_class.resource_type}"
    if "id" in body:
        verb = "PUT"
        api_path = f"{api_path}/{body['id']}"
        if entity_class == PatientRelation:
            verb = "PATCH"
            body = body["patches"]

    cheaders = clients[host]._fhir_version_headers()
    if verb == "PATCH":
        cheaders["Content-Type"] = cheaders["Content-Type"].replace(
            "application/fhir", "application/json-patch"
        )

    success, result = clients[host].send_request(
        verb, api_path, json=body, headers=cheaders
    )

    if (
        (not success)
        and (verb == "PUT")
        and (
            "no resource with this ID exists"
            in result.get("response", {})
            .get("issue", [{}])[0]
            .get("diagnostics", "")
        )
    ):
        verb = "POST"
        api_path = f"{host}/{entity_class.resource_type}"
        success, result = clients[host].send_request(
            verb, api_path, json=body, headers=cheaders
        )

    if success:
        return result["response"]["id"]
    else:
        raise RequestException(
            f"Sent {verb} request to {api_path}:\n{pformat(body)}"
            f"\nGot:\n{pformat(result)}"
        )
