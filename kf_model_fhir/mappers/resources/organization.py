"""
This module converts Kids First investigators to FHIR Organizations.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = 'Organization'


def yield_organizations(eng, table):
    for row in make_select(
            eng, table,
            CONCEPT.INVESTIGATOR.INSTITUTION
        ):
        institution = get(row, CONCEPT.INVESTIGATOR.INSTITUTION)

        if not institution:
            continue

        retval = {
            'resourceType': RESOURCE_TYPE,
            'id': make_identifier(RESOURCE_TYPE, institution),
            'meta': {
                'profile': [
                    'http://hl7.org/fhir/StructureDefinition/Organization'
                ]
            },
            'name': institution
        }

        yield retval, institution
