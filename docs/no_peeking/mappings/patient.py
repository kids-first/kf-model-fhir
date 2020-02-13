def individual_texonomy(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-taxonomy.html
    """
    if x == constants.SPECIES.DOG:
        return {
            'code': 'NCBITaxon_9615',
            'display': 'Canis lupus familiaris'
        }
    elif x == constants.SPECIES.HUMAN:
        return {
            'code': 'NCBITaxon_9606',
            'display': 'Homo sapiens'
        }
    else: 
        raise Exception('Unknown Patient individual-taxonomy')

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
        raise Exception('Unknown Patient gender')


patient = {
    'resourceType': 'Patient'
    'id': PARTICIPANT.TARGET_SERVICE_ID,
    'individual-age': {
        'valueAge':  PARTICIPANT.ENROLLMENT_AGE_DAYS
    },
    'individual-karyotypic-sex': None,
    'individual-taxonomy': {
        'coding': [
            individual_texonomy(PARTICIPANT.SPECIES or constants.SPECIES.HUMAN)
        ]
    },
    'identifier': [
        {
            'system': None,
            'value': PARTICIPANT.ID
        }
    ],
    'gender': gender(PARTICIPANT.GENDER),
    'birthDate': None
}
