def group_type(x):
    """
    http://hl7.org/fhir/R4/valueset-group-type.html
    """
    if x in {constants.SPECIES.DOG}:
        return 'animal'
    elif x == constants.SPECIES.HUMAN:
        return 'person'
    else:
        raise Exception('Unknown Group type')

def family_member_type(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-family-member-type.html
    """
    if x == constants.COMMON.TRUE:
        return {
            'code': 'proband',
            'display': 'Proband'
        }
    elif x == constants.COMMON.FALSE:
        return {
            'code': 'relative',
            'display': 'Relative'
        }
    else:
        raise Exception('Unknown Group family-member-type')


group = 'Group': {
    'resourceType': 'Group',
    'id': FAMILY.TARGET_SERVICE_ID,
    'identifier': [
        {
            'system': None
            'value': FAMILY.ID
        }
    ],
    'type': group_type(PARTICIPANT.SPECIES or constants.SPECIES.HUMAN),
    'actual': constants.COMMON.TRUE or constants.COMMON.FALSE, # defaults to True
    'member': [
        {
            'id': PARTICIPANT.ID,
            'family-member-type': {
                'coding': [
                    family_member_type(PARTICIPANT.IS_PROBAND)
                ]
            },
            # 'family-member-phenopacket': {},
            'entity': {
                'reference': f'Patient/{PARTICIPANT.KF_ID}',
                'type': 'Patient'
            },
        }
    ]
}
