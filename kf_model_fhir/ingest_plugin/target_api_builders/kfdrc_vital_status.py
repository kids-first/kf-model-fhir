"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular participant vital status data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import flexible_age, not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

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

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        not_none(record[CONCEPT.OUTCOME.VITAL_STATUS])
        patient_id = not_none(get_target_id_from_record(Patient, record))

        key_components = {
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
            "subject": {"reference": f"{Patient.resource_type}/{patient_id}"},
        }

        event_age_days = flexible_age(
            record, CONCEPT.OUTCOME.EVENT_AGE_DAYS, CONCEPT.OUTCOME.EVENT_AGE
        )
        if event_age_days:
            key_components.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/age-at-event",
                    "valueAge": {
                        "value": int(event_age_days),
                        "unit": "d",
                        "system": "http://unitsofmeasure.org",
                        "code": "days",
                    },
                }
            )

        return key_components

    @classmethod
    def query_target_ids(cls, host, key_components):
        pass

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        vital_status = record[CONCEPT.OUTCOME.VITAL_STATUS]

        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-vital-status"
                ]
            },
            "identifier": [],
            "status": "preliminary",
            "valueCodeableConcept": {
                "coding": [clinical_status[vital_status]],
                "text": vital_status,
            },
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
