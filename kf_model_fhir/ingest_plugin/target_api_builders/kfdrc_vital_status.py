"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular participant vital status data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join

clinical_status = {
    constants.OUTCOME.VITAL_STATUS.ALIVE: {
        "code": "438949009",
        "system": "http://snomed.info/sct",
        "display": "Alive",
    },
    constants.OUTCOME.VITAL_STATUS.DEAD: {
        "code": "419099009",
        "system": "http://snomed.info/sct",
        "display": "Dead",
    },
    constants.COMMON.UNKNOWN: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
        "code": "NI",
        "display": "No information",
    },
}


class VitalStatus:
    class_name = "vital_status"
    resource_type = "Observation"
    target_id_concept = CONCEPT.OUTCOME.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        assert None is not record[CONCEPT.OUTCOME.VITAL_STATUS]
        return record.get(CONCEPT.OUTCOME.UNIQUE_KEY) or join(
            record[CONCEPT.PARTICIPANT.ID],
            record[CONCEPT.OUTCOME.VITAL_STATUS],
            record.get(CONCEPT.OUTCOME.EVENT_AGE_DAYS),
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        vital_status = record.get(CONCEPT.OUTCOME.VITAL_STATUS)
        event_age_days = record.get(CONCEPT.PHENOTYPE.EVENT_AGE_DAYS)

        entity = {
            "resourceType": VitalStatus.resource_type,
            "id": get_target_id_from_record(VitalStatus, record),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-vital-status"
                ]
            },
            "identifier": [
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(VitalStatus.resource_type, study_id, key),
                }
            ],
            "status": "preliminary",
            "code": {
                "coding": [
                    {
                        "code": "263493007",
                        "system": "http://snomed.info/sct",
                        "display": "Clinical status",
                    }
                ],
                "text": "Clinical status",
            },
            "subject": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },
            "valueCodeableConcept": {
                "coding": [clinical_status[vital_status]],
                "text": vital_status,
            },
        }

        if event_age_days:
            entity.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/age-at-event",
                    "valueAge": {
                        "value": int(event_age_days),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days",
                    },
                }
            )

        return entity
