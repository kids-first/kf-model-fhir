"""
This module maps Kids First family_relationship to Phenopackets PedigreeNode (derived from FHIR FamilyMemberHistory).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PedigreeNode.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT


def affected_status(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-AffectedStatus.html
    """
    if x == constants.COMMON.FALSE:
        return {
            'system': 'http://ga4gh.org/fhir/phenopackets/CodeSystem/AffectedStatus',
            'code': 'Affected',
            'display': 'Affected'
        }
    elif x == constants.COMMON.TRUE:
        return {
            'system': 'http://ga4gh.org/fhir/phenopackets/CodeSystem/AffectedStatus',
            'code': 'unaffected',
            'display': 'Unaffected'
        }
    elif x == constants.COMMON.UNKNOWN:
        return {
            'system': 'http://ga4gh.org/fhir/phenopackets/CodeSystem/AffectedStatus',
            'code': 'missing',
            'display': 'Missing'
        }
    else:
        raise Exception('Unknown PedigreeNode AffectedStatus')

def pedigree_node_status(x):
    """
    http://hl7.org/fhir/R4/valueset-history-status.html
    """
    pass

def relationship(x):
    """
    http://hl7.org/fhir/R4/v3/FamilyMember/vs.html
    """
    if x == constants.RELATIONSHIP.FATHER:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v3-RoleCode',
            'code': 'FTH',
            'display': 'father'
        }
    elif x == constants.RELATIONSHIP.MOTHER:
        return {
            'system': 'http://terminology.hl7.org/CodeSystem/v3-RoleCode',
            'code': 'MTH',
            'display': 'mother'
        }
    else:
        raise Exception('Unknown PedigreeNode relationship')

def sex(x):
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
        raise Exception('Unknown FamilyMemberHistory sex')


pedigree_node = {
    'resourceType': 'FamilyMemberHistory',
    'id': CONCEPT.FAMILY_RELATIONSHIP.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.org/fhir/phenopackets/StructureDefinition/PedigreeNode']
    },
    'extension': [
        {
            'text': 'AffectedStatus',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/AffectedStatus',
            'valueCoding': [
                affected_status(CONCEPT.PARTICIPANT.IS_AFFECTED_UNDER_STUDY)
            ]
        },
        {
            'text': 'FamilyIdentifier',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/FamilyIdentifier',
            'valueIdentifier': [
                {
                    'system': 'https://kf-api-dataservice.kidsfirstdrc.org/families',
                    'value': CONCEPT.FAMILY.TARGET_SERVICE_ID
                },
                {
                    'value': CONCEPT.FAMILY.ID
                }
            ]
        },
        {
            'text': 'IndividualReference',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/IndividualReference',
            'valueReference': {
                'reference': f'Individual/{CONCEPT.FAMILY_RELATIONSHIP.PERSON1.TARGET_SERVICE_ID}',
                'type': 'Individual',
                'identifier': [
                    {
                        'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                        'value': CONCEPT.FAMILY_RELATIONSHIP.PERSON1.TARGET_SERVICE_ID
                    },
                    {
                        'value': CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID
                    }
                ],
                'display': CONCEPT.FAMILY_RELATIONSHIP.PERSON1.ID
            }
        }
    ],
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/family-relationships',
            'value': CONCEPT.FAMILY_RELATIONSHIP.TARGET_SERVICE_ID
        },
        {
            'value': CONCEPT.FAMILY_RELATIONSHIP.ID
        }
    ],
    'status': None, # pedigree_node_status()
    'patient': {
        'reference': f'Individual/{CONCEPT.FAMILY_RELATIONSHIP.PERSON2.TARGET_SERVICE_ID}',
        'type': 'Individual',
        'identifier': [
            {
                'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                'value': CONCEPT.FAMILY_RELATIONSHIP.PERSON2.TARGET_SERVICE_ID
            },
            {
                'value': CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID
            }
        ],
        'display': CONCEPT.FAMILY_RELATIONSHIP.PERSON2.ID
    },
    'relationship': {
        'coding': [
            relationship(CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2)
        ],
        'text': CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
    },
    'sex': sex(CONCEPT.PARTICIPANT.GENDER),
}
