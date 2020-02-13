def pedigree_node_affected_status(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-pedigree-affected-status.html
    """
    if x == constants.COMMON.FALSE:
        return {
            'code': 'Affected',
            'display': 'Affected'
        }
    elif x == constants.COMMON.TRUE:
        return {
            'code': 'unaffected',
            'display': 'Unaffected'
        }
    elif x == constants.COMMON.UNKNOWN:
        return {
            'code': 'missing',
            'display': 'Missing'
        }
    else:
        raise Exception('Unknown FamilyMemberHistory pedigree-node-affected-status')

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
        raise Exception('Unknown FamilyMemberHistory relationship')

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


family_member_history = {
    'resourceType': 'FamilyMemberHistory',
    'id': FAMILY_RELATIONSHIP.TARGET_SERVICE_ID,
    'pedigree-node-affected-status': 
        pedigree_node_affected_status(PARTICIPANT.IS_AFFECTED_UNDER_STUDY),
    'pedigree-node-family-identifier': [
        {
            'system': None,
            'value': FAMILY.ID
        }
    ],
    'pedigree-node-individual': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient'
    },
    'identifier': [
        {
            'system': None
            'value': FAMILY_RELATIONSHIP.ID
        }
    ],
    'status': None,
    'patient': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient'
    },
    'relationship': {
        "coding": [
            relationship(FAMILY_RELATIONSHIP.RELATION_FROM_1_TO_2)
        ]
        },
    'sex': sex(PARTICIPANT.GENDER),
}
