"""
This module maps Kids First diagnosis to Phenopackets Disease (derived from FHIR Condition).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Disease.html
    for the detailed structure definition.
"""

def coded_onset(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-Onset.html
    """
    pass

def tumor_stage(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-TumorStage.html
    """
    pass

def disease_code(x):
    """
    http://hl7.org/fhir/R4/valueset-condition-code.html
    """
    pass

def body_site(x):
    """
    http://hl7.org/fhir/R4/valueset-body-site.html
    """
    pass


disease =  {
    'resourceType': 'Condition',
    'id': DIAGNOSIS.TARGET_SERVICE_ID,
    'meta: {
        'profile': ['http://ga4gh.fhir.phenopackets/StructureDefinition/Disease']
    },
    'extension': [
        {
            'text': 'CodedOnset',
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/CodedOnset',
            'valueCodeableConcept': {
                'coding': [
                    {
                        'system': 'http://purl.obolibrary.org/obo/hp.owl',
                        'code': 'HP:0410280',
                        'display': 'Pediatric onset'
                    }
                ]
            }
        }
    ],
    'identifier': [
        {
            'system': 'https://kf-api-dataservice.kidsfirstdrc.org/diagnoses',
            'value': DIAGNOSIS.TARGET_SERVICE_ID
        },
        {
            'value': DIAGNOSIS.ID
        }
    ],
    'code': {
        'coding': None,	# condition_code()
        'text':	DIAGNOSIS.NAME
    },
    'bodySite': None # body_site()
    'subject': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient',
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
    'onsetAge': DIAGNOSIS.EVENT_AGE_DAYS
}
