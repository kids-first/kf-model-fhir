"""
This module converts Kids First Outcomes to FHIR kfdrc-vital-status
(derived from FHIR Observation).
"""

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "Observation"

clinical_status = {
    constants.OUTCOME.VITAL_STATUS.ALIVE: {
        "code": "438949009",
        "system": "http://snomed.info/sct",
        "display": "Alive",
    },
    constants.OUTCOME.VITAL_STATUS.DEAD: {
        "code": "419099009",
        "system": "http://snomed.info/sct",
        "display": "Dead",
    },
    constants.COMMON.UNKNOWN: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
        "code": "NI",
        "display": "No information",
    },
}


def yield_kfdrc_vital_statuses(eng, table, study_id, kfdrc_patients):
    for row in make_select(
        eng,
        table,
        CONCEPT.PARTICIPANT.ID,
        CONCEPT.OUTCOME.EVENT_AGE_DAYS,
        CONCEPT.OUTCOME.VITAL_STATUS,
    ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        event_age_days = get(row, CONCEPT.OUTCOME.EVENT_AGE_DAYS)
        vital_status = get(row, CONCEPT.OUTCOME.VITAL_STATUS)
        status = clinical_status.get(vital_status)

        if not participant_id or not status:
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(
                RESOURCE_TYPE, participant_id, vital_status, event_age_days
            ),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-vital-status"
                ]
            },
            "status": "preliminary",
            "code": {
                "coding": [
                    {
                        "code": "263493007",
                        "system": "http://snomed.info/sct",
                        "display": "Clinical status",
                    }
                ],
                "text": "Clinical status",
            },
            "subject": {
                "reference": f'Patient/{kfdrc_patients[participant_id]["id"]}'
            },
            "valueCodeableConcept": {"coding": [status], "text": vital_status},
        }

        if event_age_days:
            retval.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/age-at-event",
                    "valueAge": {
                        "value": int(event_age_days),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days",
                    },
                }
            )

        yield retval
