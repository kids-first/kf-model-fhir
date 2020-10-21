"""
Builds FHIR Condition resources (https://www.hl7.org/fhir/condition.html) from
rows of tabular participant diagnosis data.
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import (
    flexible_age,
    not_none,
    submit,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)


class Condition:
    class_name = "condition"
    resource_type = "Condition"
    target_id_concept = CONCEPT.DIAGNOSIS.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        diagnosis_name = not_none(record[CONCEPT.DIAGNOSIS.NAME])
        patient_id = not_none(get_target_id_from_record(Patient, record))

        key_components = {
            "code": {"text": diagnosis_name},
            "subject": {"reference": f"{Patient.resource_type}/{patient_id}"},
        }

        event_age_days = flexible_age(
            record,
            CONCEPT.DIAGNOSIS.EVENT_AGE_DAYS,
            CONCEPT.DIAGNOSIS.EVENT_AGE,
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
        icd_id = record.get(CONCEPT.DIAGNOSIS.ICD_ID)
        mondo_id = record.get(CONCEPT.DIAGNOSIS.MONDO_ID)
        ncit_id = record.get(CONCEPT.DIAGNOSIS.NCIT_ID)

        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-condition"
                ]
            },
            "identifier": [],
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
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        if icd_id:
            entity["code"].setdefault("coding", []).append(
                {"system": "http://hl7.org/fhir/sid/icd-10", "code": icd_id}
            )

        if mondo_id:
            entity["code"].setdefault("coding", []).append(
                {
                    "system": "http://purl.obolibrary.org/obo/mondo.owl",
                    "code": mondo_id,
                }
            )

        if ncit_id:
            entity["code"].setdefault("coding", []).append(
                {
                    "system": "http://purl.obolibrary.org/obo/ncit.owl",
                    "code": ncit_id,
                }
            )

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
