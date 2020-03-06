"""
This module maps Kids First diagnosis to Phenopackets Disease (derived from FHIR Condition).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Disease.html
for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .individual import resource_type as iRType
from .shared import get, codeable_concept, make_identifier, make_select, GO_AWAY_SERVER

resource_type = "Condition"


def disease_term_coding(x, name):
    if x.startswith("MONDO"):
        return "http://fhir.kids-first.io/CodeSystem/disease-term-mondo"
    elif x.startswith("NCIT"):
        return "http://fhir.kids-first.io/CodeSystem/disease-term-ncit"
    else:
        raise Exception(f"No {name} codings found for {x}")


def yield_diseases(eng, table, study_id, individuals):
    for row in make_select(
            eng, table,
            CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.DIAGNOSIS.NAME,
            CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS,
            CONCEPT.DIAGNOSIS.MONDO_ID,
            CONCEPT.DIAGNOSIS.NCIT_ID
        ):
        kfid = get(row, CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID)
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        name = get(row, CONCEPT.DIAGNOSIS.NAME)
        age = get(row, CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS)
        mondo_id = get(row, CONCEPT.DIAGNOSIS.MONDO_ID)
        ncit_id = get(row, CONCEPT.DIAGNOSIS.NCIT_ID)

        if not (subject_id and name) or not (mondo_id and ncit_id):
            continue

        retval = {
            "resourceType": resource_type,
            "text": {
                "status": "empty",
                "div": GO_AWAY_SERVER
            },
            "id": make_identifier(resource_type, study_id, subject_id, name, age),
            "meta": {
                "profile": ["http://ga4gh.org/fhir/phenopackets/StructureDefinition/Disease"]
            },
            "extension": [
                {
                    # https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-onset.html
                    "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/CodedOnset",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://purl.obolibrary.org/obo/hp.owl",
                                "code": "HP:0410280",
                                "display": "Pediatric onset"
                            }
                        ]
                    }
                }
            ],
            "subject": {
                "reference": f"{iRType}/{individuals[subject_id]['id']}"
            },
        }

        if kfid:
            retval["identifier"].append(
                {
                    "system": "http://kf-api-dataservice.kidsfirstdrc.org/diagnoses", "value": kfid
                }
            )

        term = {
            "url": "http://fhir.kids-first.io/StructureDefinition/disease-term",
            "valueCodeableConcept": {"text": name}
        }
        for code in {mondo_id, ncit_id}:
            if code != 'No Match':
                term["valueCodeableConcept"].setdefault("coding", []).append(
                    {
                        "system": disease_term_coding(code, "Disease Code"),
                        "code": code
                    }
                )
        retval["extension"].append(term)

        if age: 
            retval['onsetAge'] = {
                "value": int(age),
                "unit": "d",
                "system": "http://unitsofmeasure.org",
                "code": "days"
            }

        yield retval
