"""
Adds family relationship links between Patient resources from rows of tabular
participant family data.
"""
import pandas as pd

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

# https://www.hl7.org/fhir/v3/FamilyMember/vs.html
relation_dict = {
    constants.RELATIONSHIP.MOTHER: {
        "url": "relation",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "MTH",
                    "display": "mother",
                }
            ],
            "text": constants.RELATIONSHIP.MOTHER,
        },
    },
    constants.RELATIONSHIP.FATHER: {
        "url": "relation",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "FTH",
                    "display": "father",
                }
            ],
            "text": constants.RELATIONSHIP.FATHER,
        },
    },
    constants.RELATIONSHIP.CHILD: {
        "url": "relation",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "CHILD",
                    "display": "child",
                }
            ],
            "text": constants.RELATIONSHIP.CHILD,
        },
    },
}


class PatientRelation:
    class_name = "family_relationship"
    resource_type = "Patient"
    target_id_concept = CONCEPT.FAMILY_RELATIONSHIP.TARGET_SERVICE_ID

    @staticmethod
    def transform_records_list(records_list):
        df = (
            pd.DataFrame(records_list)
            .get(
                [
                    CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID,
                    CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID,
                    CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2,
                ]
            )
            .drop_duplicates()
        )
        transformed_records = [
            {"p2": i, "relationship_group": group.to_dict("records")}
            for i, group in df.groupby(CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID)
        ]
        return transformed_records

    @staticmethod
    def build_key(record):
        assert None is not record["p2"]
        return record["p2"]

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        p2 = record["p2"]
        p2id = get_target_id_from_record(Patient, {CONCEPT.PARTICIPANT.ID: p2})

        patches = []
        for r in record["relationship_group"]:
            p1 = r[CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID]
            p1id = get_target_id_from_record(
                Patient, {CONCEPT.PARTICIPANT.ID: p1}
            )
            patches.append(
                {
                    "op": "add",
                    "path": "/extension/0",
                    "value": {
                        "url": "http://fhir.kids-first.io/StructureDefinition/relation",
                        "extension": [
                            {
                                "url": "subject",
                                "valueReference": {
                                    "reference": f"Patient/{p1id}"
                                },
                            },
                            relation_dict[
                                r[
                                    CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
                                ]
                            ],
                        ],
                    },
                }
            )

        return {"id": p2id, "patches": patches}
