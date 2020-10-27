"""
Builds FHIR Condition resources (https://www.hl7.org/fhir/condition.html) from
rows of tabular participant diagnosis data.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join, make_safe_identifier


class Condition:
    class_name = "condition"
    resource_type = "Condition"
    target_id_concept = CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        assert None is not record[CONCEPT.DIAGNOSIS.NAME]
        return record.get(CONCEPT.DIAGNOSIS.UNIQUE_KEY) or join(
            record[CONCEPT.PARTICIPANT.ID],
            record[CONCEPT.DIAGNOSIS.NAME],
            record.get(CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS),
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        diagnosis_name = record.get(CONCEPT.DIAGNOSIS.NAME)
        event_age_days = record.get(CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS)
        ncit_id = record.get(CONCEPT.DIAGNOSIS.NCIT_ID)

        entity = {
            "resourceType": Condition.resource_type,
            "id": make_safe_identifier(
                get_target_id_from_record(Condition, record)
            ),
            "meta": {
                "profile": [
                    "http://fhir.ncpi-project-forge.io/StructureDefinition/ncpi-disease"
                ]
            },
            "identifier": [
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Condition.resource_type, study_id, key),
                }
            ],
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active",
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed",
                    }
                ],
                "text": "Affected",
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis",
                        }
                    ]
                }
            ],
            "code": {
                "text": diagnosis_name
            },
            "subject": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },
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

        if ncit_id:
            entity["code"].setdefault("coding", []).append(
                {
                    "system": "http://purl.obolibrary.org/obo/ncit.owl",
                    "code": ncit_id
                }
            )

        return entity
