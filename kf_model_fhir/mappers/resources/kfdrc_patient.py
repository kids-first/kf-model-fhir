"""
This module converts Kids First participants to FHIR kfdrc-patient
(derived from FHIR Patient).
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = 'Patient'


# https://hl7.org/fhir/us/core/ValueSet-omb-ethnicity-category.html
omb_ethnicity_category = {
    constants.ETHNICITY.HISPANIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2135-2',
            'display': 'Hispanic or Latino'
        }
    },
    constants.ETHNICITY.NON_HISPANIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2186-5',
            'display': 'Not Hispanic or Latino'
        }
    }
}

# https://hl7.org/fhir/us/core/ValueSet-omb-race-category.html
omb_race_category = {
    constants.RACE.NATIVE_AMERICAN: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '1002-5',
            'display': 'American Indian or Alaska Native'
        }
    },
    constants.RACE.ASIAN: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2028-9',
            'display': 'Asian'
        }
    },
    constants.RACE.BLACK: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2054-5',
            'display': 'Black or African American'
        }
    },
    constants.RACE.PACIFIC: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2076-8',
            'display': 'Native Hawaiian or Other Pacific Islander'
        }
    },
    constants.RACE.WHITE: {
        'url': 'ombCategory',
        'valueCoding': {
            'system': 'urn:oid:2.16.840.1.113883.6.238',
            'code': '2106-3',
            'display': 'White'
        }
    }
}

species_dict = {
    constants.SPECIES.DOG: {
        'url': 'http://fhir.kids-first.io/StructureDefinition/species',
        "valueCodeableConcept": {
            "coding": [
                {
                    "code": "448771007",
                    "display": "Canis lupus subspecies familiaris",
                    "definition": "Domestic dog."
                }
            ],
            "text": constants.SPECIES.DOG
        }
    },
    constants.SPECIES.HUMAN: {
        'url': 'http://fhir.kids-first.io/StructureDefinition/species',
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://fhir.kids-first.io/CodeSystem/species",
                    "code": "337915000",
                    "display": "Homo sapiens"
                }
            ],
            "text": constants.SPECIES.HUMAN
        }
    }
}

# http://hl7.org/fhir/R4/codesystem-administrative-gender.html
administrative_gender = {
    constants.GENDER.MALE: 'male',
    constants.GENDER.FEMALE: 'female',
    constants.COMMON.OTHER: 'other',
    constants.COMMON.UNKNOWN: 'unknown'
}


def yield_kfdrc_patients(eng, table, study_id):
    for row in make_select(
            eng, table,
            CONCEPT.PARTICIPANT.ID,
            CONCEPT.PARTICIPANT.ETHNICITY,
            CONCEPT.PARTICIPANT.RACE,
            CONCEPT.PARTICIPANT.SPECIES,
            CONCEPT.PARTICIPANT.GENDER
        ):
        participant_id = get(row, CONCEPT.PARTICIPANT.ID)
        ethnicity = get(row, CONCEPT.PARTICIPANT.ETHNICITY)
        race = get(row, CONCEPT.PARTICIPANT.RACE)
        species = get(row, CONCEPT.PARTICIPANT.SPECIES)
        gender = get(row, CONCEPT.PARTICIPANT.GENDER)

        if not participant_id: 
            continue

        retval = {
            'resourceType': RESOURCE_TYPE,
            'id': make_identifier(RESOURCE_TYPE, study_id, participant_id),
            'meta': {
                'profile': [
                    'http://fhir.kids-first.io/StructureDefinition/kfdrc-patient'
                ]
            },
            'identifier': [
                {
                    'system': f'https://kf-api-dataservice.kidsfirstdrc.org/participants?study_id={study_id}&external_id=', 
                    'value': participant_id
                }
            ]
        }

        if ethnicity:
            if omb_ethnicity_category.get(ethnicity):
                retval.setdefault('extension', []).append(
                    {
                        'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity',
                        'extension': [
                            omb_ethnicity_category[ethnicity],
                            {
                                'url': 'text',
                                'valueString': ethnicity
                            }
                        ]
                    }
                )

        if race:
            if omb_race_category.get(race):
                retval.setdefault('extension', []).append(
                    {
                        'url': 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race',
                        'extension': [
                            omb_race_category[race],
                            {
                                'url': 'text',
                                'valueString': race
                            }
                        ]
                    }
                )

        if species:
            if species_dict.get(species):
                retval.setdefault('extension', []).append(species_dict[species])

        if gender:
            if administrative_gender.get(gender):
                retval['gender'] = administrative_gender[gender]

        yield retval, participant_id
