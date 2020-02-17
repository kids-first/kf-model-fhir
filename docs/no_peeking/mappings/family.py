"""
This module maps Kids First family to Phenopackets Family (derived from FHIR Group).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Family.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT


def family_type(x):
    """
    http://hl7.org/fhir/R4/valueset-group-type.html
    """
    if x in {constants.SPECIES.DOG}:
        return 'animal'
    elif x == constants.SPECIES.HUMAN:
        return 'person'
    else:
        raise Exception('Unknown Family type')

def family_member_type(x):
    """
    https://www.hl7.org/fhir/v3/FamilyMember/vs.html
    """
    coding = {'system': 'http://terminology.hl7.org/CodeSystem/v3-RoleCode'}
    if x == constants.COMMON.TRUE:
        return coding.update({
            'code': 'CHILD',
            'display': 'child'
        })
    elif x == constants.RELATIONSHIP.FATHER:
        return coding.update({
            'code': 'FTH',
            'display': 'father'
        })
    elif x == constants.RELATIONSHIP.MOTHER:
        return coding.update({
            'code': 'MTH',
            'display': 'mother'
        })
    else:
        raise Exception('Unknown Family family-member-type')

def family_member_phenopacket(x): pass


family = {
    'resourceType': 'Group',
    'id': CONCEPT.FAMILY.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.fhir.phenopackets/StructureDefinition/Family']
    },
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/families',
            'value': CONCEPT.FAMILY.TARGET_SERVICE_ID
        },
        {
            'value': CONCEPT.FAMILY.ID
        }
    ],
    'extension': [
        {
            'text': 'PedigreeNodeReference',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/PedigreeNodeReference',
            'valueReference': None
        }
    ],
    'type': family_type(CONCEPT.PARTICIPANT.SPECIES or constants.SPECIES.HUMAN),
    'actual': constants.COMMON.TRUE, # defaults to True
    'member': [
        {
            'id': CONCEPT.PARTICIPANT.TARGET_SERVICE_ID,
            'extension': [
                {
                    'text': 'family-member-type',
                    'id': CONCEPT.FAMILY_RELATIONSHIP.TARGET_SERVICE_ID,
                    'url': 'family-member-type',
                    'valueCodeableConcept': {
                        'coding': [
                            family_member_type(
                                CONCEPT.PARTICIPANT.IS_PROBAND or
                                CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
                            )
                        ],
                        'text': constants.RELATIONSHIP.CHILD
                                if CONCEPT.PARTICIPANT.IS_PROBAND
                                else CONCEPT.FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
                    }
                }
            ],
            'entity': {
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
            }
        }
    ]   
}
