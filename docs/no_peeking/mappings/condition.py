def disease_onset(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-onset.html
    """
    pass

def disease_tumor_stage(x):
    """
    https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-tumor-stage.html
    """
    pass

def condition_code(x):
    """
    http://hl7.org/fhir/R4/valueset-condition-code.html
    """
    pass

def body_site(x):
    """
    http://hl7.org/fhir/R4/valueset-body-site.html
    """


condition =  {
    'resourceType': 'Condition',
    'id': DIAGNOSIS.TARGET_SERVICE_ID
    'disease-onset': {
        'coding': [
            {
                'system': 'http://purl.obolibrary.org/obo/hp.owl',
                'code': 'HP:0410280'
                'display': 'Pediatric onset'

            }
        ]
    },
    'disease-tumor-stage': None, # disease_tumor_stage()
    'code': {
        'coding': None,	# condition_code()
        'text':	DIAGNOSIS.NAME
    },
    'bodySite': None # body_site()
    'subject': {
        'reference': f'Patient/{PARTICIPANT.TARGET_SERVICE_ID}',
        'type': 'Patient'
    },
    'onsetAge': DIAGNOSIS.EVENT_AGE_DAYS
}
