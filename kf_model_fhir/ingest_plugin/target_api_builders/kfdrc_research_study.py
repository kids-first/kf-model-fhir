"""
Builds FHIR ResearchStudy resources (https://www.hl7.org/fhir/researchstudy.html)
from rows of tabular study metadata.
"""
import pandas as pd

from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.organization import (
    Organization,
)
from kf_model_fhir.ingest_plugin.target_api_builders.practitioner import (
    Practitioner,
)
from kf_model_fhir.ingest_plugin.target_api_builders.family import Family
from kf_model_fhir.ingest_plugin.shared import join, make_identifier


class ResearchStudy:
    class_name = "research_study"
    resource_type = "ResearchStudy"
    target_id_concept = CONCEPT.STUDY.TARGET_SERVICE_ID

    @staticmethod
    def transform_records_list(records_list):
        df = pd.DataFrame(records_list)
        transformed_records = records_list
        family_ids = list(df.get(CONCEPT.FAMILY.ID, []))
        for tr in transformed_records:
            tr["families"] = [
                {CONCEPT.FAMILY.ID: family_id} for family_id in family_ids
            ]

        return transformed_records

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.STUDY.ID]
        assert None is not record[CONCEPT.INVESTIGATOR.NAME]
        assert None is not record[CONCEPT.INVESTIGATOR.INSTITUTION]
        assert None is not record[CONCEPT.STUDY.NAME]
        return record.get(CONCEPT.STUDY.UNIQUE_KEY) or join(
            record[CONCEPT.STUDY.ID]
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        institution = record.get(CONCEPT.INVESTIGATOR.INSTITUTION)
        investigator_name = record.get(CONCEPT.INVESTIGATOR.NAME)
        study_name = record.get(CONCEPT.STUDY.NAME)
        attribution = record.get(CONCEPT.STUDY.ATTRIBUTION)
        short_name = record.get(CONCEPT.STUDY.SHORT_NAME)
        families = record.get("families")

        entity = {
            "resourceType": ResearchStudy.resource_type,
            "id": make_identifier(study_id),
            "meta": {
                "profile": [
                    "http://fhir.kf-strides.org/StructureDefinition/kfdrc-research-study"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kf-strides.org/studies?external_id=",
                    "value": study_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(ResearchStudy.resource_type, key),
                },
            ],
            "extension": [
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/related-organization",
                    "extension": [
                        {
                            "url": "organization",
                            "valueReference": {
                                "reference": f"Organization/{make_identifier(Organization.resource_type, institution)}"
                            },
                        }
                    ],
                }
            ],
            "title": study_name,
            "status": "completed",
            "principalInvestigator": {
                "reference": f"Practitioner/{make_identifier(Practitioner.resource_type, investigator_name)}"
            },
        }

        if attribution:
            entity["identifier"].append({"value": attribution})

        if short_name:
            entity["extension"].append(
                {
                    "url": "http://fhir.kf-strides.org/StructureDefinition/display-name",
                    "valueString": short_name,
                }
            )

        if families:
            entity["enrollment"] = [
                {
                    "reference": f"{Family.resource_type}/{get_target_id_from_record(Family, family)}"
                }
                for family in families
            ]

        return entity
