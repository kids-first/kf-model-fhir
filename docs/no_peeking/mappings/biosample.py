"""
This module maps Kids First biospecimen to Phenopackets Biosample (derived from FHIR Specimen).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Biosample.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .individual import resource_type as iRType
from .shared import get, coding

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


def make_biosample(row, study_id, individuals):
    id = get(row, CONCEPT.BIOSPECIMEN.ID)
    subject_id = get(row, CONCEPT.PARTICIPANT.ID)
    kfid = get(row, CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID)
    volume_ul = get(row, CONCEPT.BIOSPECIMEN.VOLUME_UL)
    composition = get(row, CONCEPT.BIOSPECIMEN.COMPOSITION)
    visible = get(row, CONCEPT.BIOSPECIMEN.VISIBLE)

    if not (id and subject_id):
        return None

    retval = {
        "resourceType": resource_type,
        "id": f"{resource_type}:{study_id}:{id}",
        "meta": {
            "profile": ["http://ga4gh.fhir.phenopackets/StructureDefinition/Biosample"]
        },
        "identifier": [{"system": study_id, "value": id}],
        "accessionIdentifier": [{"system": study_id, "value": id}],
        "status": biosample_status[visible or constants.COMMON.TRUE],
    }

    if subject_id:
        retval["subject"] = {
            "type": "Individual",
            "identifier": individuals[subject_id]['identifier'],
            "display": individuals[subject_id]['id'],
        }

    if volume_ul:
        retval.setdefault("collection", {})["quantity"] = {
            "unit": "uL",
            "value": volume_ul,
        }

    if composition:
        retval["type"] = coding(
            composition, [v2_0487_compositions], "Biosample Composition"
        )

    return retval
