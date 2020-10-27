"""
Builds FHIR Organization resources (https://www.hl7.org/fhir/organization.html)
from rows of tabular sequencing center data.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.shared import join, make_safe_identifier


class SequencingCenter:
    class_name = "sequencing_center"
    resource_type = "Organization"
    target_id_concept = CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID]
        return join(record[CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID])

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        sequencing_center_target_service_id = record.get(
            CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID
        )
        sequencing_center_name = record.get(CONCEPT.SEQUENCING.CENTER.NAME)

        entity = {
            "resourceType": SequencingCenter.resource_type,
            "id": make_safe_identifier(
                get_target_id_from_record(SequencingCenter, record)
            ),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Organization"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-centers",
                    "value": sequencing_center_target_service_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(SequencingCenter.resource_type, key),
                },
            ],
        }

        if sequencing_center_name:
            entity["identifier"].append(
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-centers?name=",
                    "value": sequencing_center_name,
                }
            )
            entity["name"] = sequencing_center_name

        return entity
