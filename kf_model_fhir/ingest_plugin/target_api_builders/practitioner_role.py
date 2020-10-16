"""
Builds FHIR PractitionerRole resources (https://www.hl7.org/fhir/practitionerrole.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.organization import (
    Organization,
)
from kf_model_fhir.ingest_plugin.target_api_builders.practitioner import (
    Practitioner,
)


class PractitionerRole:
    class_name = "practitioner_role"
    resource_type = "PractitionerRole"
    target_id_concept = CONCEPT.INVESTIGATOR.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        return {
            "practitioner": {
                "reference": f"{Practitioner.resource_type}/{not_none(get_target_id_from_record(Practitioner, record))}"
            },
            "organization": {
                "reference": f"{Organization.resource_type}/{not_none(get_target_id_from_record(Organization, record))}"
            },
            "code": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/practitioner-role",
                            "code": "researcher",
                            "display": "Researcher",
                        }
                    ]
                }
            ],
        }

    @classmethod
    def query_target_ids(cls, host, key_components):
        pass

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/PractitionerRole"
                ]
            },
            "identifier": [],
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        investigator_id = record.get(CONCEPT.INVESTIGATOR.ID)
        if investigator_id:
            entity["identifier"].append(
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/investigators?",
                    "value": f"external_id={investigator_id}",
                }
            )

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
