"""
This module converts Kids First investigators to FHIR PractitionerRoles.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = 'PractitionerRole'


def yield_practitioner_roles(eng, table, practitioners, organizations):
    for row in make_select(
            eng, table,
            CONCEPT.INVESTIGATOR.ID,
            CONCEPT.INVESTIGATOR.INSTITUTION,
            CONCEPT.INVESTIGATOR.NAME
        ):
        investigator_id = get(row, CONCEPT.INVESTIGATOR.ID)
        institution = get(row, CONCEPT.INVESTIGATOR.INSTITUTION)
        name = get(row, CONCEPT.INVESTIGATOR.NAME)
        
        if not all((institution, name)):
            continue

        retval = {
            'resourceType': RESOURCE_TYPE,
            'id': make_identifier(RESOURCE_TYPE, institution, name),
            'meta': {
                'profile': [
                    'http://hl7.org/fhir/StructureDefinition/PractitionerRole'
                ]
            },
            'practitioner': {
                'reference': f'Practitioner/{practitioners[name]["id"]}'
            },
            'organization': {
                'reference': f'Organization/{organizations[institution]["id"]}'
            },
            'code': [
                {
                    'coding': [ 
                        {
                            'system': 'http://terminology.hl7.org/CodeSystem/practitioner-role',
                            'code': 'researcher',
                            'display': 'Researcher'
                        }
                    ]
                }
            ]
        }

        if investigator_id:
            retval.setdefault('identifier', []).append(
                {
                    'system': f'https://kf-api-dataservice.kidsfirstdrc.org/investigators?external_id=', 
                    'value': investigator_id
                }
            )

        yield retval, (institution, name)
