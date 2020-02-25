"""
This module maps Kids First phenotype to Phenopackets PhenotypicFeature (derived from FHIR Observation).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PhenotypicFeature.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .individual import resource_type as iRType
from .shared import get, codeable_concept, make_identifier, make_select, GO_AWAY_SERVER

# http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
v3_observation_interpretation_coding = {
    constants.PHENOTYPE.OBSERVED.NO: {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'code': 'NEG',
        'display': 'Negative'
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'code': 'POS',
        'display': 'Positive'
    }
}

resource_type = "Observation"

def yield_phenotypic_features(eng, table, study_id, individuals):
    for row in make_select(
        eng, table, CONCEPT.PARTICIPANT.ID, CONCEPT.PHENOTYPE.NAME, CONCEPT.PHENOTYPE.OBSERVED, CONCEPT.PHENOTYPE.EVENT_AGE_DAYS
    ):
        subject_id = get(row, CONCEPT.PARTICIPANT.ID)
        phenotype_name = get(row, CONCEPT.PHENOTYPE.NAME)
        phenotype_observed = get(row, CONCEPT.PHENOTYPE.OBSERVED)
        phenotype_age = get(row, CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)

        if not (subject_id and phenotype_name and (phenotype_observed in v3_observation_interpretation_coding)):
            continue

        retval = {
            'resourceType': resource_type,
            "text": {
                "status": "empty",
                "div": GO_AWAY_SERVER
            },
            'id': make_identifier(resource_type, study_id, subject_id, phenotype_age, phenotype_name),
            'meta': {
                'profile': ['http://ga4gh.org/fhir/phenopackets/StructureDefinition/PhenotypicFeature']
            },
            'status': 'registered',
            'code': {
                'text': phenotype_name,
                'coding': []
            },
            'interpretation': [
                codeable_concept(
                    phenotype_observed, [v3_observation_interpretation_coding], "Phenotype Observed"
                )
            ],
            'subject': {
                "reference": f"Patient/{individuals[subject_id]['id']}"
            }
        }

        if phenotype_age:
            # HOW DO I ADD AGE AT OBSERVATION?
            pass

        yield retval
