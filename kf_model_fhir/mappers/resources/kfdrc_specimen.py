"""
This module converts Kids First biospecimens to FHIR kfdrc-specimen
(derived from FHIR Specimen).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "Specimen"


# https://www.hl7.org/fhir/v2/0487/index.html
specimen_type = {
    constants.SPECIMEN.COMPOSITION.BLOOD: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "BLD",
        "display": "Whole blood",
    },
    constants.SPECIMEN.COMPOSITION.SALIVA: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "SAL",
        "display": "Saliva",
    },
    constants.SPECIMEN.COMPOSITION.TISSUE: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "TISS",
        "display": "Tissue",
    },
}


def yield_kfdrc_specimens(eng, table, study_id, kfdrc_patients):
    for row in make_select(
        eng,
        table,
        CONCEPT.PARTICIPANT.ID,
        CONCEPT.BIOSPECIMEN.ID,
        CONCEPT.BIOSPECIMEN.EVENT_AGE_DAYS,
        CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML,
        CONCEPT.BIOSPECIMEN.COMPOSITION,
        CONCEPT.BIOSPECIMEN.VOLUME_UL,
    ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        biospecimen_id = get(row, CONCEPT.BIOSPECIMEN.ID)
        event_age_days = get(row, CONCEPT.BIOSPECIMEN.EVENT_AGE_DAYS)
        concentration_mg_per_ml = get(
            row, CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML
        )
        composition = get(row, CONCEPT.BIOSPECIMEN.COMPOSITION)
        volume_ul = get(row, CONCEPT.BIOSPECIMEN.VOLUME_UL)

        if not all((participant_id, biospecimen_id)):
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(RESOURCE_TYPE, study_id, biospecimen_id),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-specimen"
                ]
            },
            "identifier": [
                {
                    "system": f"http://kf-api-dataservice.kf-strides.org/biospecimens?study_id={study_id}&external_aliquot_id=",
                    "value": biospecimen_id,
                }
            ],
            "subject": {
                "reference": f'Patient/{kfdrc_patients[participant_id]["id"]}'
            },
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

        if concentration_mg_per_ml:
            retval.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/concentration",
                    "valueQuantity": {
                        "value": float(concentration_mg_per_ml),
                        "unit": "mg/mL",
                    },
                }
            )

        if composition:
            retval["type"] = {
                "coding": [specimen_type[composition]],
                "text": composition,
            }

        if volume_ul:
            retval.setdefault("collection", {})["quantity"] = {
                "unit": "uL",
                "value": float(volume_ul),
            }

        yield retval, biospecimen_id
