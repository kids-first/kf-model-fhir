"""
Builds FHIR Group resources (https://www.hl7.org/fhir/group.html) from rows
of tabular data.
"""
import pandas as pd
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

group_type = {
    constants.SPECIES.DOG: "animal",
    constants.SPECIES.HUMAN: "person",
}


class Family:
    class_name = "family"
    resource_type = "Group"
    target_id_concept = CONCEPT.FAMILY.TARGET_SERVICE_ID

    @classmethod
    def transform_records_list(cls, records_list):
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

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        study_id = not_none(record[CONCEPT.STUDY.TARGET_SERVICE_ID])
        family_id = not_none(record[CONCEPT.FAMILY.ID])
        return {
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/families?",
                    "value": f"study_id={study_id}&external_id={family_id}",
                },
            ],
        }

    @classmethod
    def query_target_ids(cls, host, key_components):
        pass

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        species = record.get(CONCEPT.PARTICIPANT.SPECIES)
        study_id = record[CONCEPT.STUDY.TARGET_SERVICE_ID]
        participants = [
            {
                CONCEPT.STUDY.TARGET_SERVICE_ID: study_id,
                CONCEPT.PARTICIPANT.ID: not_none(p),
            }
            for p in record.get("participants")
        ]
        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Group"]
            },
            "type": group_type.get(species) or "person",
            "actual": True,
            "member": [
                {
                    "entity": {
                        "reference": f"{Patient.resource_type}/{get_target_id_from_record(Patient, p)}"
                    }
                }
                for p in participants
            ],
        }
        return {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
