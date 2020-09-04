"""
Builds FHIR Patient resources (https://www.hl7.org/fhir/patient.html) from rows
of tabular participant data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.shared import join

# https://hl7.org/fhir/us/core/ValueSet-omb-ethnicity-category.html
omb_ethnicity_category = {
    constants.ETHNICITY.HISPANIC: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2135-2",
            "display": "Hispanic or Latino",
        },
    },
    constants.ETHNICITY.NON_HISPANIC: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2186-5",
            "display": "Not Hispanic or Latino",
        },
    },
}

# https://hl7.org/fhir/us/core/ValueSet-omb-race-category.html
omb_race_category = {
    constants.RACE.NATIVE_AMERICAN: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "1002-5",
            "display": "American Indian or Alaska Native",
        },
    },
    constants.RACE.ASIAN: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2028-9",
            "display": "Asian",
        },
    },
    constants.RACE.BLACK: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2054-5",
            "display": "Black or African American",
        },
    },
    constants.RACE.PACIFIC: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2076-8",
            "display": "Native Hawaiian or Other Pacific Islander",
        },
    },
    constants.RACE.WHITE: {
        "url": "ombCategory",
        "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2106-3",
            "display": "White",
        },
    },
}

species_dict = {
    constants.SPECIES.DOG: {
        "url": "http://fhir.kf-strides.org/StructureDefinition/species",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://fhir.kf-strides.org/CodeSystem/species",
                    "code": "448771007",
                    "display": "Canis lupus subspecies familiaris",
                }
            ],
            "text": constants.SPECIES.DOG,
        },
    },
    constants.SPECIES.HUMAN: {
        "url": "http://fhir.kf-strides.org/StructureDefinition/species",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://fhir.kf-strides.org/CodeSystem/species",
                    "code": "337915000",
                    "display": "Homo sapiens",
                }
            ],
            "text": constants.SPECIES.HUMAN,
        },
    },
}

# http://hl7.org/fhir/R4/codesystem-administrative-gender.html
administrative_gender = {
    constants.GENDER.MALE: "male",
    constants.GENDER.FEMALE: "female",
    constants.COMMON.OTHER: "other",
    constants.COMMON.UNKNOWN: "unknown",
}


class Patient:
    class_name = "patient"
    resource_type = "Patient"
    target_id_concept = CONCEPT.PARTICIPANT.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        return record.get(CONCEPT.PARTICIPANT.UNIQUE_KEY) or join(
            record[CONCEPT.PARTICIPANT.ID]
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        participant_id = record.get(CONCEPT.PARTICIPANT.ID)
        ethnicity = record.get(CONCEPT.PARTICIPANT.ETHNICITY)
        race = record.get(CONCEPT.PARTICIPANT.RACE)
        species = record.get(CONCEPT.PARTICIPANT.SPECIES)
        gender = record.get(CONCEPT.PARTICIPANT.GENDER)

        entity = {
            "resourceType": Patient.resource_type,
            "id": get_target_id_from_record(Patient, record),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-patient"
                ]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kf-strides.org/participants?study_id={study_id}&external_id=",
                    "value": participant_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Patient.resource_type, study_id, key),
                },
            ],
        }

        if ethnicity:
            if omb_ethnicity_category.get(ethnicity):
                entity.setdefault("extension", []).append(
                    {
                        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                        "extension": [
                            omb_ethnicity_category[ethnicity],
                            {"url": "text", "valueString": ethnicity},
                        ],
                    }
                )

        if race:
            if omb_race_category.get(race):
                entity.setdefault("extension", []).append(
                    {
                        "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                        "extension": [
                            omb_race_category[race],
                            {"url": "text", "valueString": race},
                        ],
                    }
                )

        if species:
            if species_dict.get(species):
                entity.setdefault("extension", []).append(species_dict[species])

        if gender:
            if administrative_gender.get(gender):
                entity["gender"] = administrative_gender[gender]

        return entity
