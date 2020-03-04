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
            eng, table, 
            CONCEPT.BIOSPECIMEN.ID,
            CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.BIOSPECIMEN.COMPOSITION,
            CONCEPT.BIOSPECIMEN.VOLUME_UL,
            CONCEPT.BIOSPECIMEN.VISIBLE
        ):
        id = get(row, CONCEPT.BIOSPECIMEN.ID)
        kfid = get(row, CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID)
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        composition = get(row, CONCEPT.BIOSPECIMEN.COMPOSITION)
        volume_ul = get(row, CONCEPT.BIOSPECIMEN.VOLUME_UL)
        visible = get(row, CONCEPT.BIOSPECIMEN.VISIBLE)

        if not (id and subject_id):
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
            "identifier": [
                {
                    "system": f"http://kf-api-dataservice.kidsfirstdrc.org/biospecimens?study_id={study_id}", "value": id
                }
            ],
            "status": biosample_status[visible or constants.COMMON.TRUE],
            "subject": {
                "reference": f"{iRType}/{individuals[subject_id]['id']}"
            },
        }

        if kfid:
            retval["identifier"].append(
                {
                    "system": "http://kf-api-dataservice.kidsfirstdrc.org/biospecimens", "value": kfid
                }
            )

        if composition:
            retval["type"] = codeable_concept(
                composition, [v2_0487_compositions], "Biosample Composition"
            )

        if volume_ul:
            retval.setdefault("collection", {})["quantity"] = {
                "unit": "uL",
                "value": float(volume_ul),
            }

        yield retval, id
