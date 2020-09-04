"""
Builds FHIR Practitioner resources (https://www.hl7.org/fhir/practitioner.html)
from rows of tabular investigator metadata.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.shared import join, make_identifier


class Practitioner:
    class_name = "practitioner"
    resource_type = "Practitioner"
    target_id_concept = None

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.INVESTIGATOR.NAME]
        return join(record[CONCEPT.INVESTIGATOR.NAME])

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        investigator_name = record.get(CONCEPT.INVESTIGATOR.NAME)

        return {
            "resourceType": Practitioner.resource_type,
            "id": make_identifier(
                Practitioner.resource_type, investigator_name
            ),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Practitioner"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kf-strides.org/investigators?name=",
                    "value": investigator_name,
                }
            ],
            "name": [{"text": investigator_name}],
        }
