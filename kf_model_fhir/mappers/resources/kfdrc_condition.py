"""
This module converts Kids First diagnoses to FHIR kfdrc-condition
(derived from FHIR Condition).
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "Condition"


def yield_kfdrc_conditions(eng, table, study_id, kfdrc_patients):
    for row in make_select(
        eng,
        table,
        CONCEPT.PARTICIPANT.ID,
        CONCEPT.DIAGNOSIS.NAME,
        CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS,
        CONCEPT.DIAGNOSIS.MONDO_ID,
        CONCEPT.DIAGNOSIS.NCIT_ID,
        CONCEPT.DIAGNOSIS.ICD_ID,
    ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        name = get(row, CONCEPT.DIAGNOSIS.NAME)
        event_age_days = get(row, CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS)
        mondo = get(row, CONCEPT.DIAGNOSIS.MONDO_ID)
        ncit = get(row, CONCEPT.DIAGNOSIS.NCIT_ID)
        icd = get(row, CONCEPT.DIAGNOSIS.ICD_ID)

        if not all((participant_id, name)):
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(
                RESOURCE_TYPE, study_id, participant_id, name, event_age_days
            ),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-condition"
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis",
                        }
                    ]
                }
            ],
            "code": {"text": name},
            "subject": {
                "reference": f'Patient/{kfdrc_patients[participant_id]["id"]}'
            },
        }

        if event_age_days:
            retval.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/age-at-event",
                    "valueAge": {
                        "value": int(event_age_days),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days",
                    },
                }
            )

        if mondo:
            retval["code"].setdefault("coding", []).append(
                {
                    "system": "http://purl.obolibrary.org/obo/mondo.owl",
                    "code": mondo,
                }
            )

        if ncit:
            retval["code"].setdefault("coding", []).append(
                {"system": "http://purl.obolibrary.org/obo/ncit.owl", "code": ncit}
            )

        if icd:
            retval["code"].setdefault("coding", []).append(
                {"system": "http://hl7.org/fhir/sid/icd-10", "code": icd}
            )

        yield retval
