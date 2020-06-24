"""
Builds FHIR PractitionerRole resources (https://www.hl7.org/fhir/practitionerrole.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.practitioner import (
    Practitioner,
)
from kf_model_fhir.ingest_plugin.target_api_builders.organization import (
    Organization,
)
from kf_model_fhir.ingest_plugin.shared import join, make_identifier


class PractitionerRole:
    class_name = "practitioner_role"
    resource_type = "PractitionerRole"
    target_id_concept = CONCEPT.INVESTIGATOR.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.INVESTIGATOR.NAME]
        assert None is not record[CONCEPT.INVESTIGATOR.INSTITUTION]
        return record.get(CONCEPT.INVESTIGATOR.UNIQUE_KEY) or join(
            record[CONCEPT.INVESTIGATOR.NAME],
            record[CONCEPT.INVESTIGATOR.INSTITUTION],
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        investigator_id = record.get(CONCEPT.INVESTIGATOR.ID)
        investigator_name = record.get(CONCEPT.INVESTIGATOR.NAME)
        institution = record.get(CONCEPT.INVESTIGATOR.INSTITUTION)

        entity = {
            "resourceType": PractitionerRole.resource_type,
            "id": get_target_id_from_record(PractitionerRole, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/PractitionerRole"
                ]
            },
            "identifier": [
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(PractitionerRole.resource_type, key),
                }
            ],
            "practitioner": {
                "reference": f"Practitioner/{make_identifier(Practitioner.resource_type, investigator_name)}"
            },
            "organization": {
                "reference": f"Organization/{make_identifier(Organization.resource_type, institution)}"
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

        if investigator_id:
            entity["identifier"].append(
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/investigators?external_id=",
                    "value": investigator_id,
                }
            )

        return entity
