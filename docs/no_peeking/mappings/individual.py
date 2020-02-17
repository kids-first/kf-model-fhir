"""
This module maps Kids First participant to Phenopackets Individual (derived from FHIR Patient).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Individual.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT


def karyotypic_sex(x):
    """
    http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex
    """
    coding = {'system': 'http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex'}
    if x == constants.GENDER.FEMALE:
        return coding.update({
            'code': 'XX',
            'display': 'Female'
        })
    elif x == constants.GENDER.MALE:
        return coding.update({
            'code': 'XY',
            'display': 'Male'
        })
    elif x == constants.COMMON.OTHER:
        return coding.update({
            'code': 'OTHER_KARYOTYPE',
            'display': 'None of the above types'
        })
    elif x == constants.COMMON.UNKNOWN:
        return coding.update({
            'code': 'UNKNOWN_KARYOTYPE',
            'display': 'Untyped or inconclusive karyotyping'
        })
    else:
        raise Exception('Unknown Individual KaryotypicSex')

def taxonomy(x):
    """
    http://purl.obolibrary.org/obo/ncbitaxon.owl
    """
    coding = {'system': 'http://purl.obolibrary.org/obo/ncbitaxon.owl'}
    if x == constants.SPECIES.DOG:
        return coding.update({
            'code': 'NCBITaxon:9615',
            'display': 'Canis lupus familiaris'
        })
    elif x == constants.SPECIES.HUMAN:
        return coding.update({
            'code': 'NCBITaxon:9606',
            'display': 'Homo sapiens'
        })
    else: 
        raise Exception('Unknown Individual Taxonomy')

def gender(x):
    """
    http://hl7.org/fhir/R4/valueset-administrative-gender.html
    """
    if x == constants.GENDER.FEMALE:
        return 'female'
    elif x == constants.GENDER.MALE:
        return 'male'
    elif x == constants.COMMON.OTHER:
        return 'other'
    elif x == constants.COMMON.UNKNOWN:
        return 'unknown'
    else:
        raise Exception('Unknown Individual gender')


individual = {
    'resourceType': 'Patient',
    'id': CONCEPT.PARTICIPANT.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.fhir.phenopackets/StructureDefinition/Individual']
    },
    'extension': [
        {
            'text': 'KaryotypicSex',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/KaryotypicSex',
            'valueCodeableConcept': {
                'coding': [
                    karyotypic_sex(CONCEPT.PARTICIPANT.GENDER)
                ],
                'text': CONCEPT.PARTICIPANT.GENDER
            }
        },
        {
            'text': 'Taxonomy',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/Taxonomy',
            'valueCodeableConcept': {
                'coding': [
                    taxonomy(CONCEPT.PARTICIPANT.SPECIES or constants.SPECIES.HUMAN)
                ],
                'text': CONCEPT.PARTICIPANT.SPECIES or constants.SPECIES.HUMAN
            }
        }
    ],
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
            'value': CONCEPT.PARTICIPANT.TARGET_SERVICE_ID
        },
        {
            'value': CONCEPT.PARTICIPANT.ID
        }
    ],
    'gender': gender(CONCEPT.PARTICIPANT.GENDER)
}
