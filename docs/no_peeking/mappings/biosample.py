"""
This module maps Kids First biospecimen to Phenopackets Biosample (derived from FHIR Specimen).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Biosample.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT


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
    if x == constants.SPECIMEN.COMPOSITION.BLOOD:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
            'code': 'BLD',
            'display': 'Whole blood'
        }
    elif x == constants.SPECIMEN.COMPOSITION.SALIVA:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
            'code': 'SAL',
            'display': 'Saliva'
        }
    elif x == constants.SPECIMEN.COMPOSITION.TISSUE:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v2-0487',
            'code': 'TISS',
            'display': 'Tissue'
        }
    else:
        raise Exception('Unknown Biosample type')


biosample = {
    'resourceType': 'Specimen',
    'id': CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.fhir.phenopackets/StructureDefinition/Biosample']
    },
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/biospecimens',
            'value': CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID
        },
        {
            'value': CONCEPT.BIOSPECIMEN.ID
        }
    ],
    'accessionIdentifier': [
        {
            'value': CONCEPT.BIOSPECIMEN.ID
        }
    ],
    'status': biosample_status(CONCEPT.BIOSPECIMEN.VISIBLE),
    'type': {
        'coding': [
            biosample_type(CONCEPT.BIOSPECIMEN.COMPOSITION)
        ],
        'text': CONCEPT.BIOSPECIMEN.COMPOSITION
    },
    'subject': {
        'reference': f'Individual/CONCEPT.{PARTICIPANT.TARGET_SERVICE_ID}',
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
    'collection': {
        'quantity': {
            'value': CONCEPT.BIOSPECIMEN.VOLUME_UL,
            'unit': 'uL'
        }
    }
}
