"""
This module maps Kids First biospecimen to Phenopackets Biosample (derived from FHIR Specimen).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Biosample.html
    for the detailed structure definition.
"""

def biosample_status(x):
    """
    http://hl7.org/fhir/R4/valueset-specimen-status.html
    """
    if x == constants.COMMON.FALSE:
        return 'unavailable'
    elif x == constants.COMMON.TRUE:
        return 'available'
    else:
        raise Exception('Unknown Biosample status')

def biosample_type(x):
    """
    http://terminology.hl7.org/ValueSet/v2-0487
    """
    coding = {'system': 'http://terminology.hl7.org/CodeSystem/v2-0487'}
    if x == constants.SPECIMEN.COMPOSITION.BLOOD:
        return coding.update({
            'code': 'BLD',
            'display': 'Whole blood'
        })
    elif x == constants.SPECIMEN.COMPOSITION.SALIVA:
        return coding.update({
            'code': 'SAL',
            'display': 'Saliva'
        })
    elif x == constants.SPECIMEN.COMPOSITION.TISSUE:
        return coding.update({
            'code': 'TISS',
            'display': 'Tissue'
        })
    else:
        raise Exception('Unknown Biosample type')


biosample = {
    'resourceType': 'Specimen',
    'id': BIOSPECIMEN.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.fhir.phenopackets/StructureDefinition/Biosample']
    },
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/biospecimens',
            'value': BIOSPECIMEN.TARGET_SERVICE_ID
        },
        {
            'value': BIOSPECIMEN.ID
        }
    ],
    'accessionIdentifier': [
        {
            'value': BIOSPECIMEN.ID
        }
    ],
    'status': biosample_status(BIOSPECIMEN.VISIBLE),
    'type': {
        'coding': [
            biosample_type(BIOSPECIMEN.COMPOSITION)
        ],
        'text': BIOSPECIMEN.COMPOSITION
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
    'collection': {
        'quantity': {
            'value': BIOSPECIMEN.VOLUME_UL,
            'unit': 'uL'
        }
    }
}
