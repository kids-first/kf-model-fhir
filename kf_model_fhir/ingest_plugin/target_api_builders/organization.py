"""
Builds FHIR Organization resources (https://www.hl7.org/fhir/organization.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit


class Organization:
    class_name = "organization"
    resource_type = "Organization"
    target_id_concept = None

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        return {
            "identifier": [
                {
                    "system": "organization",
                    "value": not_none(record[CONCEPT.INVESTIGATOR.INSTITUTION]),
                }
            ],
        }

    @classmethod
    def query_target_ids(cls, host, key_components):
        pass

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        return {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Organization"
                ]
            },
            "name": record[CONCEPT.INVESTIGATOR.INSTITUTION],
        }

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
