"""
Builds FHIR Organization resources (https://www.hl7.org/fhir/organization.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.shared import join, make_identifier


class Organization:
    class_name = "organization"
    resource_type = "Organization"
    target_id_concept = None

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.INVESTIGATOR.INSTITUTION]
        return join(record[CONCEPT.INVESTIGATOR.INSTITUTION])

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        institution = record.get(CONCEPT.INVESTIGATOR.INSTITUTION)

        return {
            "resourceType": Organization.resource_type,
            "id": make_identifier(Organization.resource_type, institution),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Organization"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/investigators?institution=",
                    "value": institution,
                }
            ],
            "name": institution,
        }
