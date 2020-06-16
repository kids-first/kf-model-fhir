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
        "url": "http://fhir.kids-first.io/StructureDefinition/species",
        "valueCodeableConcept": {
            "coding": [
                {
                    "code": "448771007",
                    "display": "Canis lupus subspecies familiaris",
                    "definition": "Domestic dog.",
                }
            ],
            "text": constants.SPECIES.DOG,
        },
    },
    constants.SPECIES.HUMAN: {
        "url": "http://fhir.kids-first.io/StructureDefinition/species",
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://fhir.kids-first.io/CodeSystem/species",
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
    resource_type = 'Patient'
    api_path = f"/{resource_type}"
    target_id_concept = CONCEPT.PARTICIPANT.TARGET_SERVICE_ID

    @staticmethod
    def build_key(row):
        assert None is not row[CONCEPT.PARTICIPANT.ID]
        return row.get(CONCEPT.PARTICIPANT.UNIQUE_KEY) or join(
            row[CONCEPT.PARTICIPANT.ID]
        )

    @staticmethod
    def build_entity(row, key, get_target_id_from_row):
        study_id = row[CONCEPT.STUDY.ID]
        participant_id = row.get(CONCEPT.PARTICIPANT.ID)
        ethnicity = row.get(CONCEPT.PARTICIPANT.ETHNICITY)
        race = row.get(CONCEPT.PARTICIPANT.RACE)
        species = row.get(CONCEPT.PARTICIPANT.SPECIES)
        gender = row.get(CONCEPT.PARTICIPANT.GENDER)

        entity = {
            "resourceType": Patient.resource_type,
            "id": get_target_id_from_row(Patient, row),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-patient"
                ]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kidsfirstdrc.org/participants?study_id={study_id}&external_id=",
                    "value": participant_id,
                },
                {
                    "system": f"urn:kids-first:unique-string",
                    "value": join(Patient.resource_type, study_id, key),
                },
            ],
            "gender": administrative_gender.get(gender),
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

        return entity
