"""
This module converts Kids First diagnoses to FHIR kfdrc-condition-no-phi
(derived from FHIR Condition).
"""
from common.utils import get, make_identifier, make_select
from kf_lib_data_ingest.common.concept_schema import CONCEPT


def yield_diagnoses(eng, table, study_id, participants):
    for row in make_select(
            eng, table,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS,
            CONCEPT.DIAGNOSIS.NAME,
            CONCEPT.DIAGNOSIS.MONDO_ID,
            CONCEPT.DIAGNOSIS.NCIT_ID,
            CONCEPT.DIAGNOSIS.ICD_ID
        ):
        event_age_days = get(row, CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS)
        name = get(row, CONCEPT.DIAGNOSIS.NAME)
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        mondo = get(row, CONCEPT.DIAGNOSIS.MONDO_ID)
        ncit = get(row, CONCEPT.DIAGNOSIS.NCIT_ID)
        icd = get(row, CONCEPT.DIAGNOSIS.ICD_ID)

        if not all(name, participant_id):
            continue

        retval = {
            'resourceType': 'Condition',
            'meta': {
                'profile': [
                    'http://fhir.kids-first.io/StructureDefinition/kfdrc-condition-no-phi'
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                        }
                    ]
                }
            ],
            'id': make_identifier('condition', study_id,
                        participant_id, name,
                        event_age_days),
            'code': {
                'text': name
            },
            'subject': {
                'reference': f'Patient/{participants[participant_id]["id"]}'
            }
        }

        if event_age_days:
            retval.setdefault('extension', []).append({
                'url': 'http://fhir.kids-first.io/StructureDefinition/age-at-event',
                'valueAge': {
                    'value': int(event_age_days),
                    'unit': 'd',
                    'system': 'http://unitsofmeasure.org',
                    'code': 'days'
                }
            })

        if mondo:
            retval['code'].setdefault('coding', []).append({
                "system": "http://purl.obolibrary.org/obo/mondo.owl",
                "code": mondo
            })

        if ncit:
            retval['code'].setdefault('coding', []).append({
                "system": "http://ncit.nci.nih.gov",
                "code": ncit
            })

        if icd:
            retval['code'].setdefault('coding', []).append({
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": icd
            })

        yield retval
