"""
Builds FHIR Specimen resources (https://www.hl7.org/fhir/specimen.html)
from rows of tabular participant biospecimen adata.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join

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

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        assert None is not record[CONCEPT.BIOSPECIMEN.ID]
        return record.get(CONCEPT.BIOSPECIMEN.UNIQUE_KEY) or join(
            record[CONCEPT.BIOSPECIMEN.ID]
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        biospecimen_id = record.get(CONCEPT.BIOSPECIMEN.ID)
        event_age_days = record.get(CONCEPT.BIOSPECIMEN.EVENT_AGE_DAYS)
        concentration_mg_per_ml = record.get(
            CONCEPT.BIOSPECIMEN.CONCENTRATION_MG_PER_ML
        )
        composition = record.get(CONCEPT.BIOSPECIMEN.COMPOSITION)
        volume_ul = record.get(CONCEPT.BIOSPECIMEN.VOLUME_UL)

        entity = {
            "resourceType": Specimen.resource_type,
            "id": get_target_id_from_record(Specimen, record),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-specimen"
                ]
            },
            "identifier": [
                {
                    "system": f"http://kf-api-dataservice.kf-strides.org/biospecimens?study_id={study_id}&external_aliquot_id=",
                    "value": biospecimen_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Specimen.resource_type, study_id, key),
                },
            ],
            "subject": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },
        }

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

        if composition:
            entity["type"] = {
                "coding": [specimen_type[composition]],
                "text": composition,
            }

        if volume_ul:
            entity.setdefault("collection", {})["quantity"] = {
                "unit": "uL",
                "value": float(volume_ul),
            }

        return entity
