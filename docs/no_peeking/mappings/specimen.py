def status(x):
    """
    http://hl7.org/fhir/R4/valueset-specimen-status.html
    """
    if x == constants.COMMON.FALSE:
        return 'unavailable'
    elif x == constants.COMMON.TRUE:
        return 'available'
    else:
        raise Exception('Unknown Specimen status')

def specimen_type(x):
    """
    http://hl7.org/fhir/R4/v2/0487/index.html
    """
    if x == constants.SPECIMEN.COMPOSITION.BLOOD:
        return	{
            'coding': 'BLD',
            'display': 'Whole blood'
        }
    elif x == constants.SPECIMEN.COMPOSITION.SALIVA:
        return	{
            'coding': 'SAL',
            'display': 'Saliva'
        }
    elif x == constants.SPECIMEN.COMPOSITION.TISSUE:
        return	{
            'coding': 'TISS',
            'display': 'Tissue'
        }
    else:
        raise Exception('Unknown Specimen type')


specimen = {
    'resourceType': 'Specimen',
    'id': BIOSPECIMEN.TARGET_SERVICE_ID,
    'biosample-individual-age-at-collection': None,
    'biosampe-histological-diagnosis': None,
    'biosample-tumor-progression': None,
    'biosample-tumor-grade': None,
    'biosample-control': True or False, # defaults to True
    'identifier': [
        {
            'system': None,
            'value': BIOSPECIMEN.ID
        }
    ],
    'accessionIdentifier': [
        {
            'system': None,
            'value': BIOSPECIMEN.ID
        }
    ],
    'status': status(BIOSPECIMEN.VISIBLE),
    'type': {
        'coding': [
            specimen_type(BIOSPECIMEN.COMPOSITION)
        ],
        'text': BIOSPECIMEN.COMPOSITION
    },
    'subject': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient'
    },
    'collection': {
        'quantity': {
            'value': BIOSPECIMEN.VOLUME_UL
            'unit': 'uL'
        }
    }
}
