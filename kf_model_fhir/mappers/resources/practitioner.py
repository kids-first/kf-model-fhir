"""
This module converts Kids First investigators to FHIR Practitioners.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = 'Practitioner'


def yield_practitioners(eng, table):
    for row in make_select(
            eng, table,
            CONCEPT.INVESTIGATOR.NAME
        ):
        name = get(row, CONCEPT.INVESTIGATOR.NAME)

        if not name:
            continue

        retval = {
            'resourceType': RESOURCE_TYPE,
            'id': make_identifier(RESOURCE_TYPE, name),
            'meta': {
                'profile': [
                    'http://hl7.org/fhir/StructureDefinition/Practitioner'
                ]
            },
            'identifier': [
                {
                    'system': 'https://kf-api-dataservice.kidsfirstdrc.org/investigators?name=', 
                    'value': name
                }
            ],
            'name': [
                {
                    'text': name
                }
            ]
        }

        yield retval, name
