"""
This module maps Kids First phenotype to Phenopackets PhenotypicFeature (derived from FHIR Observation).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PhenotypicFeature.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT


def phenotypic_feature_status(x):
    """
    http://hl7.org/fhir/R4/valueset-observation-status.html
    """
    pass

def interpretation(x):
    """
    http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
    """
    if x == constants.PHENOTYPE.OBSERVED.NO:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
            'code': 'NEG',
            'display': 'Negative'
        }
    elif x == constants.PHENOTYPE.OBSERVED.YES:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
            'code': 'POS',
            'display': 'Positive'
        }
    else:
        raise Exception('Unknown PhenotypicFeature interpretation')


phenotypic_feature = {
    'resourceType': 'Observation',
    'meta': {
        'profile': ['http://ga4gh.org/fhir/phenopackets/StructureDefinition/PhenotypicFeature']
    },
    'id': CONCEPT.PHENOTYPE.TARGET_SERVICE_ID,
    'extension': [
        {
            'text': 'Onset',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/Onset',
            'valueAge': CONCEPT.PHENOTYPE.EVENT_AGE_DAYS
        }
    ],
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/phenotypes',
            'value': CONCEPT.PHENOTYPE.TARGET_SERVICE_ID
        },
        {
            'value': CONCEPT.PHENOTYPE.ID
        }
    ],
    'status': 'registered', # defaults to 'registered'
    'code': {
        'text': CONCEPT.PHENOTYPE.NAME
    },
    'subject': {
        'reference': f'Individual/{CONCEPT.PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Individual',
        'identifier': [
            {
                'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                'value': CONCEPT.PARTICIPANT.TARGET_SERVICE_ID
            },
            {
                'value': CONCEPT.PARTICIPANT.ID
            }
        ],
        'display': CONCEPT.PARTICIPANT.ID
    },
    'interpretation': {
        'coding': [
            interpretation(CONCEPT.PHENOTYPE.OBSERVED)
        ],
        'text': CONCEPT.PHENOTYPE.OBSERVED
    }
}
