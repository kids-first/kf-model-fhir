"""
Builds FHIR ResearchStudy resources (https://www.hl7.org/fhir/researchstudy.html)
from rows of tabular study metadata.
"""
import pandas as pd
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.family import Family
from kf_model_fhir.ingest_plugin.target_api_builders.organization import (
    Organization,
)
from kf_model_fhir.ingest_plugin.target_api_builders.practitioner import (
    Practitioner,
)


class ResearchStudy:
    class_name = "research_study"
    resource_type = "ResearchStudy"
    target_id_concept = CONCEPT.STUDY.TARGET_SERVICE_ID

    @classmethod
    def transform_records_list(cls, records_list):
        df = pd.DataFrame(records_list)
        transformed_records = records_list
        family_ids = list(df.get(CONCEPT.FAMILY.ID, []))
        for tr in transformed_records:
            tr["families"] = [
                {CONCEPT.FAMILY.ID: family_id} for family_id in family_ids
            ]

        return transformed_records

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        return {
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/studies?",
                    "value": f"external_id={not_none(record[CONCEPT.STUDY.ID])}",
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
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-research-study"
                ]
            },
            "title": record[CONCEPT.STUDY.NAME],
            "status": "completed",
        }

        entity = {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

        org_id = get_target_id_from_record(Organization, record)
        if org_id:
            entity.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/related-organization",
                    "extension": [
                        {
                            "url": "organization",
                            "valueReference": {
                                "reference": f"{Organization.resource_type}/{org_id}"
                            },
                        }
                    ],
                }
            )

        principle_investigator = get_target_id_from_record(Practitioner, record)
        if principle_investigator:
            entity["principalInvestigator"] = {
                "reference": f"{Practitioner.resource_type}/{principle_investigator}"
            }

        attribution = record.get(CONCEPT.STUDY.ATTRIBUTION)
        if attribution:
            entity["identifier"].append({"value": attribution})

        short_name = record.get(CONCEPT.STUDY.SHORT_NAME)
        if short_name:
            entity.setdefault("extension", []).append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/display-name",
                    "valueString": short_name,
                }
            )

        families = record.get("families")
        study_id = record[CONCEPT.STUDY.TARGET_SERVICE_ID]
        if families:
            for fam in families:
                fam[CONCEPT.STUDY.TARGET_SERVICE_ID] = study_id

            entity["enrollment"] = [
                {
                    "reference": f"{Family.resource_type}/{get_target_id_from_record(Family, fam)}"
                }
                for fam in families
            ]

        return entity

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
