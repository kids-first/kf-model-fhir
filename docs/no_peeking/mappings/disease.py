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


def yield_diseases(eng, table, study_id, individuals):
    for row in make_select(
            eng, table,
            CONCEPT.DIAGNOSIS.ID,
            CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.DIAGNOSIS.NAME,
            CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS
        ):
        id = get(row, CONCEPT.DIAGNOSIS.ID)
        kfid = get(row, CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID)
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        diagnosis_name = get(row, CONCEPT.DIAGNOSIS.NAME)
        event_age_days = get(row, CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS)

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
                "profile": ["http://ga4gh.org/fhir/phenopackets/StructureDefinition/Disease"]
            },
            "identifier": [
                {
                    "system": f"http://kf-api-dataservice.kidsfirstdrc.org/diagnoses?study_id={study_id}", "value": id
                }
            ]
        }

        if kfid:
            retval["identifier"].append(
                {
                    "system": "http://kf-api-dataservice.kidsfirstdrc.org/diagnoses", "value": kfid
                }
            )
        
        if subject_id:
            retval["subject"] = {
                "reference": f"Patient/{individuals[subject_id]['id']}",
                "type": iRType
            }

        if diagnosis_name:
            retval.setdefault("extension", []).append(
                {
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
            )
            retval.setdefault("code", {})["text"] = diagnosis_name
        
        if event_age_days:
            retval['onsetAge'] = f'{event_age_days}d'

        yield retval, id
