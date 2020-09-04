"""
This module converts Kids First family relationships to FHIR kfdrc-patient relations.
"""
import pandas as pd

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_select, get

RESOURCE_TYPE = "Patient"


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


def yield_kfdrc_patient_relations(eng, table, kfdrc_patients):
    df = pd.DataFrame(
        [
            dict(row)
            for row in make_select(
                eng,
                table,
                CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID,
                CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID,
                CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2,
            )
        ]
    )

    for person2_id, group in df.groupby(CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID):
        retval = kfdrc_patients.get(person2_id)
        if not retval:
            continue

        for _, row in group.iterrows():
            person1_id = get(row, CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID)
            relation = get(
                row, CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
            )

            retval.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/relation",
                    "extension": [
                        {
                            "url": "subject",
                            "valueReference": {
                                "reference": f'{RESOURCE_TYPE}/{kfdrc_patients[person1_id]["id"]}'
                            },
                        },
                        relation_dict[relation],
                    ],
                }
            )

        yield retval, person2_id
