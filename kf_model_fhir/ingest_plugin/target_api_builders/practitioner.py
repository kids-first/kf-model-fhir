"""
Builds FHIR Practitioner resources (https://www.hl7.org/fhir/practitioner.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit


class Practitioner:
    class_name = "practitioner"
    resource_type = "Practitioner"
    # PractitionerRole already uses CONCEPT.INVESTIGATOR.TARGET_SERVICE_ID,
    # so the below is set to None
    target_id_concept = None

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        investigator_name = not_none(record[CONCEPT.INVESTIGATOR.NAME])
        return {
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/investigators?",
                    "value": f"name={investigator_name}",
                }
            ],
            "name": [{"text": investigator_name}],
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
                    "http://hl7.org/fhir/StructureDefinition/Practitioner"
                ]
            },
        }
        return {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
