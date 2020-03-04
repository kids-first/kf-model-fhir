"""
This module maps Kids First phenotype to Phenopackets PhenotypicFeature (derived from FHIR Observation).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PhenotypicFeature.html
for the detailed structure definition.
"""
import os
import json

from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .individual import resource_type as iRType
from .shared import get, codeable_concept, make_identifier, make_select, GO_AWAY_SERVER

phenotypic_feature_code_coding = {
    concept["code"]: {
        "system": "http://purl.obolibrary.org/obo/hp.owl",
        "code": concept["code"],
        "display": concept["display"]
    }
    for concept in json.load(open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "phenotypic_feature_hpo_cs.json"
        )))["concept"]
}

# http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
v3_observation_interpretation_coding = {
    constants.PHENOTYPE.OBSERVED.NO: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "NEG",
        "display": "Negative"
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "POS",
        "display": "Positive"
    }
}

resource_type = "Observation"


def yield_phenotypic_features(eng, table, study_id, individuals):
    for row in make_select(
            eng, table,
            CONCEPT.PHENOTYPE.TARGET_SERVICE_ID,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.PHENOTYPE.NAME,
            CONCEPT.PHENOTYPE.OBSERVED,
            CONCEPT.PHENOTYPE.EVENT_AGE_DAYS,
            CONCEPT.PHENOTYPE.HPO_ID
        ):
        kfid = get(row, CONCEPT.PHENOTYPE.TARGET_SERVICE_ID)
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        name = get(row, CONCEPT.PHENOTYPE.NAME)
        observed = get(row, CONCEPT.PHENOTYPE.OBSERVED)
        age = get(row, CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)
        hpo_id = get(row, CONCEPT.PHENOTYPE.HPO_ID)

        if not (subject_id and name and hpo_id and
                (observed in v3_observation_interpretation_coding)):
            continue

        retval = {
            "resourceType": resource_type,
            "text": {
                "status": "empty",
                "div": GO_AWAY_SERVER
            },
            "id": make_identifier(resource_type, study_id, subject_id, name, observed, age),
            "meta": {
                "profile": ["http://ga4gh.org/fhir/phenopackets/StructureDefinition/PhenotypicFeature"]
            },
            "status": "registered",
            "code": {
                "coding": [phenotypic_feature_code_coding[hpo_id]],
                "text": name,
            },
            "subject": {
                "reference": f"{iRType}/{individuals[subject_id]['id']}"
            },
            "interpretation": [
                codeable_concept(
                    observed, 
                    [v3_observation_interpretation_coding], 
                    "Phenotype Observed"
                )
            ],
        }

        if age:
            retval.setdefault("extension", []).append(
                {
                    "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Onset",
                    "valueAge": {
                        "value": int(age),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days"
                    }
                }
            )

        yield retval
