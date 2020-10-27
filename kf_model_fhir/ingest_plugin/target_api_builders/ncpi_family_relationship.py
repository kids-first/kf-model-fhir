"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular participant family relationship data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.patient import (
    Patient,
)

from kf_model_fhir.ingest_plugin.shared import join, make_safe_identifier

# https://www.hl7.org/fhir/v3/FamilyMember/vs.html
code = {
    constants.RELATIONSHIP.MOTHER: {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "PRN",
                "display": "parent",
            },
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "MTH",
                "display": "mother",
            }
        ],
        "text": constants.RELATIONSHIP.MOTHER,
    },
    constants.RELATIONSHIP.FATHER: {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "PRN",
                "display": "parent",
            },
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "FTH",
                "display": "father",
            }
        ],
        "text": constants.RELATIONSHIP.FATHER,
    },
    constants.RELATIONSHIP.CHILD: {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                "code": "CHILD",
                "display": "child",
            }
        ],
        "text": constants.RELATIONSHIP.CHILD,
    },
}


class FamilyRelationship:
    class_name = "family_relationship"
    resource_type = "Observation"
    target_id_concept = CONCEPT.FAMILY_RELATIONSHIP.TARGET_SERVICE_ID

    @staticmethod
    def _pid(record, which, get_target_id_from_record):
        return get_target_id_from_record(
            Patient,
            {
                CONCEPT.PARTICIPANT.TARGET_SERVICE_ID: record.get(
                    which.TARGET_SERVICE_ID
                ),
                CONCEPT.PARTICIPANT.UNIQUE_KEY: record.get(which.UNIQUE_KEY),
                CONCEPT.PARTICIPANT.ID: record.get(which.ID),
            },
        )

    @staticmethod
    def build_key(record):
        p1 = (
            record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON1.TARGET_SERVICE_ID)
            or record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON1.UNIQUE_KEY)
            or record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID)
        )
        p2 = (
            record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON2.TARGET_SERVICE_ID)
            or record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON2.UNIQUE_KEY)
            or record.get(CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID)
        )
        assert p1 is not None
        assert p2 is not None
        assert (
            record[CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2] is not None
        )
        return record.get(CONCEPT.FAMILY_RELATIONSHIP.UNIQUE_KEY) or join(
            p1,
            record[
                CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
            ],
            p2,
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        p1_id = FamilyRelationship._pid(
            record,
            CONCEPT.FAMILY_RELATIONSHIP.PERSON1,
            get_target_id_from_record,
        )
        p2_id = FamilyRelationship._pid(
            record,
            CONCEPT.FAMILY_RELATIONSHIP.PERSON2,
            get_target_id_from_record,
        )
        relation_from_1_to_2 = record.get(
            CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
        )

        entity = {
            "resourceType": FamilyRelationship.resource_type,
            "id": get_target_id_from_record(FamilyRelationship, record),
            "meta": {
                "profile": [
                    "http://fhir.ncpi-project-forge.io/StructureDefinition/ncpi-family-relationship"
                ]
            },
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "FAMMEMB",
                        "display": "family member"
                    }
                ],
                "text": "Family relationship",
            },
            "subject": {
                "reference": f"Patient/{p1_id}"
            },
            "focus": [
                {
                    "reference": f"Patient/{p2_id}"
                }
            ],
            "valueCodeableConcept": code[relation_from_1_to_2],
        }

        return entity
