"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular participant phenotype data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import (
    flexible_age,
    not_none,
    submit,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

# https://www.hl7.org/fhir/valueset-observation-interpretation.html
interpretation = {
    constants.PHENOTYPE.OBSERVED.NO: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "NEG",
        "display": "Negative",
    },
    constants.PHENOTYPE.OBSERVED.YES: {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code": "POS",
        "display": "Positive",
    },
}


class Phenotype:
    class_name = "phenotype"
    resource_type = "Observation"
    target_id_concept = CONCEPT.PHENOTYPE.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        phenotype_name = not_none(record[CONCEPT.PHENOTYPE.NAME])
        patient_id = not_none(get_target_id_from_record(Patient, record))

        key_components = {
            "code": {"text": phenotype_name},
            "subject": {"reference": f"{Patient.resource_type}/{patient_id}"},
        }

        event_age_days = flexible_age(
            record,
            CONCEPT.PHENOTYPE.EVENT_AGE_DAYS,
            CONCEPT.PHENOTYPE.EVENT_AGE,
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
        observed = record.get(CONCEPT.PHENOTYPE.OBSERVED)

        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-phenotype"
                ]
            },
            "identifier": [],
            "status": "preliminary",
            "interpretation": [
                {"coding": [interpretation[observed]], "text": observed}
            ],
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        hpo_id = record.get(CONCEPT.PHENOTYPE.HPO_ID)
        if hpo_id:
            entity["code"].setdefault("coding", []).append(
                {
                    "code": hpo_id,
                }
            )

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
