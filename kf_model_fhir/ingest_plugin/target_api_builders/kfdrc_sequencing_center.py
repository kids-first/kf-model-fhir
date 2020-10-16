"""
Builds FHIR Organization resources (https://www.hl7.org/fhir/organization.html)
from rows of tabular sequencing center data.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit


class SequencingCenter:
    class_name = "sequencing_center"
    resource_type = "Organization"
    target_id_concept = CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        return {
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-centers/",
                    "value": not_none(record[cls.target_id_concept]),
                },
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
                    "http://hl7.org/fhir/StructureDefinition/Organization"
                ]
            },
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        sequencing_center_name = record.get(CONCEPT.SEQUENCING.CENTER.NAME)
        if sequencing_center_name:
            entity["identifier"].append(
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-centers?",
                    "value": f"name={sequencing_center_name}",
                }
            )
            entity["name"] = sequencing_center_name

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
