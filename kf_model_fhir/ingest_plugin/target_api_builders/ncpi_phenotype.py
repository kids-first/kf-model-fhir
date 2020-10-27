"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular participant phenotype data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join, make_safe_identifier

# https://www.hl7.org/fhir/valueset-observation-interpretation.html
interpretation = {
    constants.PHENOTYPE.OBSERVED.NO: {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "NEG",
                "display": "Negative",
            }
        ],
        "text": constants.PHENOTYPE.OBSERVED.NO,
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "POS",
                "display": "Positive",
            }
        ],
        "text": constants.PHENOTYPE.OBSERVED.YES,
    },
}


class Phenotype:
    class_name = "phenotype"
    resource_type = "Observation"
    target_id_concept = CONCEPT.PHENOTYPE.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        assert None is not record[CONCEPT.PHENOTYPE.NAME]
        assert record[CONCEPT.PHENOTYPE.OBSERVED] in interpretation
        return record.get(CONCEPT.PHENOTYPE.UNIQUE_KEY) or join(
            record[CONCEPT.PARTICIPANT.ID],
            record[CONCEPT.PHENOTYPE.NAME],
            record[CONCEPT.PHENOTYPE.OBSERVED],
            record.get(CONCEPT.PHENOTYPE.EVENT_AGE_DAYS),
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        phenotype_name = record.get(CONCEPT.PHENOTYPE.NAME)
        event_age_days = record.get(CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)
        observed = record.get(CONCEPT.PHENOTYPE.OBSERVED)
        hpo_id = record.get(CONCEPT.PHENOTYPE.HPO_ID)

        entity = {
            "resourceType": Phenotype.resource_type,
            "id": make_safe_identifier(
                get_target_id_from_record(Phenotype, record)
            ),
            "meta": {
                "profile": [
                    "http://fhir.ncpi-project-forge.io/StructureDefinition/ncpi-phenotype"
                ]
            },
            "identifier": [
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Phenotype.resource_type, study_id, key),
                }
            ],
            "status": "preliminary",
            "code": {
                "coding": [
                    {
                        "system": "http://purl.obolibrary.org/obo/hp.owl",
                        "code": hpo_id
                    }
                ], 
                "text": phenotype_name
            },
            "subject": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "373573001",
                        "display": "Clinical finding present (situation)",
                    }
                ],
                "text": "Phenotype Present",
            },
            "interpretation": [interpretation[observed]],
        }

        if event_age_days:
            entity.setdefault("extension", []).append(
                {
                    "url": "http://fhir.ncpi-project-forge.io/StructureDefinition/age-at-event",
                    "valueAge": {
                        "value": int(event_age_days),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days",
                    },
                }
            )

        return entity
