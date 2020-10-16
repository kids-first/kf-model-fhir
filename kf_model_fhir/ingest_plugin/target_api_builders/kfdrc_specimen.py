"""
Builds FHIR Specimen resources (https://www.hl7.org/fhir/specimen.html)
from rows of tabular participant biospecimen adata.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

# https://www.hl7.org/fhir/v2/0487/index.html
specimen_type = {
    constants.SPECIMEN.COMPOSITION.BLOOD: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "BLD",
        "display": "Whole blood",
    },
    constants.SPECIMEN.COMPOSITION.SALIVA: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "SAL",
        "display": "Saliva",
    },
    constants.SPECIMEN.COMPOSITION.TISSUE: {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0487",
        "code": "TISS",
        "display": "Tissue",
    },
}


class Specimen:
    class_name = "specimen"
    resource_type = "Specimen"
    target_id_concept = CONCEPT.BIOSPECIMEN.TARGET_SERVICE_ID

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        not_none(get_target_id_from_record(Patient, record))
        study_id = not_none(record[CONCEPT.STUDY.TARGET_SERVICE_ID])
        aliquot = not_none(record[CONCEPT.BIOSPECIMEN.ID])
        return {
            "identifier": [
                {
                    "system": "http://kf-api-dataservice.kidsfirstdrc.org/biospecimens?",
                    "value": f"study_id={study_id}&external_aliquot_id={aliquot}",
                },
            ],
        }

    @classmethod
    def query_target_ids(cls, host, key_components):
        pass

    @classmethod
    def build_entity(cls, record, get_target_id_from_record):
        entity = {
            "resourceType": cls.resource_type,
            "id": get_target_id_from_record(cls, record),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-specimen"
                ]
            },
            "subject": {
                "reference": f"{Patient.resource_type}/{get_target_id_from_record(Patient, record)}"
            },
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        event_age_days = record.get(CONCEPT.BIOSPECIMEN.EVENT_AGE_DAYS)
        if event_age_days:
            entity.setdefault("extension", []).append(
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

        concentration_mg_per_ml = record.get(
            CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML
        )
        if concentration_mg_per_ml:
            entity.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/concentration",
                    "valueQuantity": {
                        "value": float(concentration_mg_per_ml),
                        "unit": "mg/mL",
                    },
                }
            )

        composition = record.get(CONCEPT.BIOSPECIMEN.COMPOSITION)
        if composition:
            entity["type"] = {
                "coding": [specimen_type[composition]],
                "text": composition,
            }

        volume_ul = record.get(CONCEPT.BIOSPECIMEN.VOLUME_UL)
        if volume_ul:
            entity.setdefault("collection", {})["quantity"] = {
                "unit": "uL",
                "value": float(volume_ul),
            }

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
