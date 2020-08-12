"""
Builds FHIR Group resources (https://www.hl7.org/fhir/group.html) from rows
of tabular data.
"""
import pandas as pd

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join

group_type = {
    constants.SPECIES.DOG: "animal",
    constants.SPECIES.HUMAN: "person",
}


class Family:
    class_name = "family"
    resource_type = "Group"
    target_id_concept = CONCEPT.FAMILY.TARGET_SERVICE_ID

    @staticmethod
    def transform_records_list(records_list):
        df = pd.DataFrame(records_list)
        df[CONCEPT.FAMILY.TARGET_SERVICE_ID] = df.get(
            CONCEPT.FAMILY.TARGET_SERVICE_ID
        )
        transformed_records = [
            {
                CONCEPT.FAMILY.ID: family_id,
                CONCEPT.FAMILY.TARGET_SERVICE_ID: list(
                    group[CONCEPT.FAMILY.TARGET_SERVICE_ID]
                )[0],
                "participants": group[CONCEPT.PARTICIPANT.ID].drop_duplicates(),
            }
            for family_id, group in df.groupby(CONCEPT.FAMILY.ID)
        ]
        return transformed_records

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.FAMILY.ID]
        return record[CONCEPT.FAMILY.ID]

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        family_id = record.get(CONCEPT.FAMILY.ID)
        species = record.get(CONCEPT.PARTICIPANT.SPECIES)
        participants = [
            {CONCEPT.PARTICIPANT.ID: p} for p in record.get("participants")
        ]

        return {
            "resourceType": Family.resource_type,
            "id": get_target_id_from_record(Family, record),
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Group"]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kf-strides.org/families?study_id={study_id}&external_id=",
                    "value": family_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Family.resource_type, study_id, key),
                },
            ],
            "type": group_type.get(species) or "person",
            "actual": True,
            "member": [
                {
                    "entity": {
                        "reference": f"Patient/{get_target_id_from_record(Patient, p)}"
                    }
                }
                for p in participants
            ],
        }
