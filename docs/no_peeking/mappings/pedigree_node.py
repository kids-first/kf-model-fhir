"""
This module maps Kids First family_relationship to Phenopackets PedigreeNode (derived from FHIR FamilyMemberHistory).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-PedigreeNode.html
    for the detailed structure definition.
"""

def affected_status(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-AffectedStatus.html
    """
    coding = {'system': 'http://ga4gh.org/fhir/phenopackets/CodeSystem/AffectedStatus'}
    if x == constants.COMMON.FALSE:
        return coding.update({
            'code': 'Affected',
            'display': 'Affected'
        })
    elif x == constants.COMMON.TRUE:
        return coding.update({
            'code': 'unaffected',
            'display': 'Unaffected'
        })
    elif x == constants.COMMON.UNKNOWN:
        return coding.update({
            'code': 'missing',
            'display': 'Missing'
        })
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
    coding = {'system': 'http://terminology.hl7.org/CodeSystem/v3-RoleCode'}
    if x == constants.RELATIONSHIP.FATHER:
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
    'id': FAMILY_RELATIONSHIP.TARGET_SERVICE_ID,
    'meta': {
        'profile': ['http://ga4gh.org/fhir/phenopackets/StructureDefinition/PedigreeNode']
    },
    'extension': [
        {
            'text': 'AffectedStatus',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/AffectedStatus',
            'valueCoding': [
                affected_status(PARTICIPANT.IS_AFFECTED_UNDER_STUDY)
            ]
        },
        {
            'text': 'FamilyIdentifier',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/FamilyIdentifier',
            'valueIdentifier': [
                {
                    'system': 'https://kf-api-dataservice.kidsfirstdrc.org/families',
                    'value': FAMILY.TARGET_SERVICE_ID
                },
                {
                    'value': FAMILY.ID
                }
            ]
        },
        {
            'text': 'IndividualReference',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/IndividualReference',
            'valueReference': {
                'reference': f'Individual/{FAMILY_RELATIONSHIP.PERSON1.TARGET_SERVICE_ID}',
                'type': 'Individual',
                'identifier': [
                    {
                        'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                        'value': FAMILY_RELATIONSHIP.PERSON1.TARGET_SERVICE_ID
                    },
                    {
                        'value': FAMILY_RELATIONSHIP.PERSON1.ID
                    }
                ],
                'display': FAMILY_RELATIONSHIP.PERSON1.ID
            }
        }
    ]
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/family-relationships',
            'value': FAMILY_RELATIONSHIP.TARGET_SERVICE_ID
        },
        {
            'value': FAMILY_RELATIONSHIP.ID
        }
    ],
    'status': None, # pedigree_node_status()
    'patient': {
        'reference': f'Individual/{FAMILY_RELATIONSHIP.PERSON2.TARGET_SERVICE_ID}',
        'type': 'Individual',
        'identifier': [
            {
                'system': 'https://kf-api-dataservice.kidsfirstdrc.org/participants',
                'value': FAMILY_RELATIONSHIP.PERSON2.TARGET_SERVICE_ID
            },
            {
                'value': FAMILY_RELATIONSHIP.PERSON2.ID
            }
        ],
        'display': FAMILY_RELATIONSHIP.PERSON2.ID
    },
    'relationship': {
        'coding': [
            relationship(FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2)
        ],
        'text': FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2
    },
    'sex': sex(PARTICIPANT.GENDER),
}
