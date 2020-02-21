"""
This module maps Kids First biospecimen to Phenopackets Biosample (derived from FHIR Specimen).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Biosample.html
for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .individual import resource_type as iRType
from .shared import get, codeable_concept, make_identifier, make_select, GO_AWAY_SERVER

# http://hl7.org/fhir/R4/valueset-specimen-status.html
biosample_status = {
    constants.COMMON.FALSE: "unavailable",
    constants.COMMON.TRUE: "available",
}

# http://terminology.hl7.org/ValueSet/v2-0487
v2_0487_compositions = {
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

resource_type = "Specimen"


def yield_biosamples(eng, table, study_id, individuals):
    for row in make_select(
        eng, table, CONCEPT.BIOSPECIMEN.ID, CONCEPT.PARTICIPANT.ID, 
        CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID, CONCEPT.BIOSPECIMEN.VOLUME_UL,
        CONCEPT.BIOSPECIMEN.COMPOSITION, CONCEPT.BIOSPECIMEN.VISIBLE
    ):
        id = get(row, CONCEPT.BIOSPECIMEN.ID)
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        kfid = get(row, CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID)
        volume_ul = get(row, CONCEPT.BIOSPECIMEN.VOLUME_UL)
        composition = get(row, CONCEPT.BIOSPECIMEN.COMPOSITION)
        visible = get(row, CONCEPT.BIOSPECIMEN.VISIBLE)

        if not id:
            continue

        retval = {
            "resourceType": resource_type,
            "text": {
                "status": "empty",
                "div": GO_AWAY_SERVER
            },
            "id": make_identifier(resource_type, study_id, id),
            "meta": {
                "profile": ["http://ga4gh.org/fhir/phenopackets/StructureDefinition/Biosample"]
            },
            "identifier": [{"system": f"http://kf-api-dataservice.kidsfirstdrc.org/biospecimens?study_id={study_id}", "value": id}],
            "status": biosample_status[visible or constants.COMMON.TRUE],
        }

        if subject_id:
            retval["subject"] = {
                "reference": f"Patient/{individuals[subject_id]['id']}"
            }

        if volume_ul:
            retval.setdefault("collection", {})["quantity"] = {
                "unit": "uL",
                "value": float(volume_ul),
            }

        if composition:
            retval["type"] = codeable_concept(
                composition, [v2_0487_compositions], "Biosample Composition"
            )

        yield retval, id
