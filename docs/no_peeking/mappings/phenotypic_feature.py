"""
This module maps Kids First phenotype to Phenopackets PhenotypicFeature (derived from FHIR Observation).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PhenotypicFeature.html
    for the detailed structure definition.
"""

def phenotypic_feature_status(x):
    """
    http://hl7.org/fhir/R4/valueset-observation-status.html
    """
    pass

def interpretation(x):
    """
    http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation
    """
    coding = {'system': 'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation'}
    if x == constants.PHENOTYPE.OBSERVED.NO:
        return coding.update({
            'code': 'NEG',
            'display': 'Negative'
        })
    elif x == constants.PHENOTYPE.OBSERVED.YES:
        return coding.update({
            'code': 'POS',
            'display': 'Positive'
        })
    else:
        raise Exception('Unknown PhenotypicFeature interpretation')


phenotypic_feature = {
    'resourceType': 'Observation',
    'meta: {
        'profile': ['http://ga4gh.org/fhir/phenopackets/StructureDefinition/PhenotypicFeature']
    },
    'id': PHENOTYPE.TARGET_SERVICE_ID,
    'extension': [
        'text': 'Onset',
        'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/Onset',
        'valueAge': PHENOTYPE.EVENT_AGE_DAYS
    ],
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/phenotypes',
            'value': PHENOTYPE.TARGET_SERVICE_ID
        },
        {
            'value': PHENOTYPE.ID
        }
    ],
    'status': 'registered', # defaults to 'registered'
    'code': {
        'text': PHENOTYPE.NAME
    },
    'subject': {
        'reference': f'Individual/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Individual',
        'identifier': [
            {
                'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                'value': PARTICIPANT.TARGET_SERVICE_ID
            },
            {
                'value': PARTICIPANT.ID
            }
        ],
        'display': PARTICIPANT.ID
    },
    'interpretation': {
        'coding': [
            interpretation(PHENOTYPE.OBSERVED)
        ],
        'text': PHENOTYPE.OBSERVED
    }
}
