def status(x):
    """
    http://hl7.org/fhir/R4/valueset-observation-status.html
    """
    pass

def interpretation(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-phenotypic-feature-interpretation.html
    """
    if x == constants.PHENOTYPE.OBSERVED.NO:
        return {
            'code': 'NEG',
            'display': 'Negative'
        }
    elif x == constants.PHENOTYPE.OBSERVED.YES:
        return {
            'code': 'POS',
            'display': 'Positive'
        }
    else:
        raise Exception('Unknown Observation interpretation')


observation = {
    'id': PHENOTYPE.TARGET_SERVICE_ID,
    'phenotypic-feature-severity': None,
    'phenotypic-feature-modifier': None,
    'phenotypic-feature-onset': {
        'valueAge':  PHENOTYPE.EVENT_AGE_DAYS
    },
    'evidence': None,
    'identifier': [
        {
            'system': None,
            'value': PHENOTYPE.ID
        }
    ],
    'status': 'registered', # defaults to 'registered'
    'code': {
        'text': PHENOTYPE.NAME
    },
    'subject': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient'
    },
    'interpretation': {
        'coding': [
            interpretation(PHENOTYPE.OBSERVED)
        ]
    },
    'bodySite': None # body_site()
}
