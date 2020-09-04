"""
This module converts Kids First phenotypes to FHIR kfdrc-phenotype
(derived from FHIR Observation).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "Observation"


# https://www.hl7.org/fhir/valueset-observation-interpretation.html
interpretation = {
    constants.PHENOTYPE.OBSERVED.NO: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "NEG",
        "display": "Negative",
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "POS",
        "display": "Positive",
    },
}


def yield_kfdrc_phenotypes(eng, table, study_id, kfdrc_patients):
    for row in make_select(
        eng,
        table,
        CONCEPT.PARTICIPANT.ID,
        CONCEPT.PHENOTYPE.NAME,
        CONCEPT.PHENOTYPE.HPO_ID,
        CONCEPT.PHENOTYPE.EVENT_AGE_DAYS,
        CONCEPT.PHENOTYPE.OBSERVED,
    ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        name = get(row, CONCEPT.PHENOTYPE.NAME)
        hpo = get(row, CONCEPT.PHENOTYPE.HPO_ID)
        event_age_days = get(row, CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)
        observed = get(row, CONCEPT.PHENOTYPE.OBSERVED)

        if not all((participant_id, name, hpo)) or not interpretation.get(
            observed
        ):
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(
                RESOURCE_TYPE,
                study_id,
                participant_id,
                name,
                observed,
                event_age_days,
            ),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-phenotype"
                ]
            },
            "status": "preliminary",
            "code": {"coding": [{"code": hpo}], "text": name},
            "subject": {
                "reference": f'Patient/{kfdrc_patients[participant_id]["id"]}'
            },
            "interpretation": [
                {"coding": [interpretation[observed]], "text": observed}
            ],
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
