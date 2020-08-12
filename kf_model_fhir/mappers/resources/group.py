"""
This module converts Kids First families to FHIR Groups.
"""
import pandas as pd

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "Group"


group_type = {
    constants.SPECIES.DOG: "animal",
    constants.SPECIES.HUMAN: "person",
}


def yield_groups(eng, table, study_id, kfdrc_patients):
    df = pd.DataFrame(
        [
            dict(row)
            for row in make_select(
                eng,
                table,
                CONCEPT.FAMILY.ID,
                CONCEPT.PARTICIPANT.SPECIES,
                CONCEPT.PARTICIPANT.ID,
            )
        ]
    )

    for family_id, group in df.groupby(CONCEPT.FAMILY.ID):
        if not family_id:
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(RESOURCE_TYPE, study_id, family_id),
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Group"]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kf-strides.org/families?study_id={study_id}&external_id=",
                    "value": family_id,
                }
            ],
            "actual": True,
        }

        for _, row in group.iterrows():
            species = get(row, CONCEPT.PARTICIPANT.SPECIES)
            participant_id = get(row, CONCEPT.PARTICIPANT.ID)

            if not participant_id:
                continue

            retval["type"] = group_type.get(species) or "person"
            retval.setdefault("member", []).append(
                {
                    "entity": {
                        "reference": f'Patient/{kfdrc_patients[participant_id]["id"]}'
                    }
                }
            )

        if not isinstance(retval.get("member"), list):
            continue

        yield retval, family_id
