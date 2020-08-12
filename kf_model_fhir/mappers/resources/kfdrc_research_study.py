"""
This module converts Kids First studies to FHIR kfdrc-research-study
(derived from FHIR ResearchStudy).
"""
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from common.utils import make_identifier, make_select, get

RESOURCE_TYPE = "ResearchStudy"


def yield_kfdrc_research_studies(
    eng, table, target_service_id, organizations, practitioner_roles, groups
):
    for row in make_select(
        eng,
        table,
        CONCEPT.STUDY.ID,
        CONCEPT.INVESTIGATOR.INSTITUTION,
        CONCEPT.INVESTIGATOR.NAME,
        CONCEPT.STUDY.ATTRIBUTION,
        CONCEPT.STUDY.SHORT_NAME,
        CONCEPT.STUDY.AUTHORITY,
        CONCEPT.STUDY.NAME,
    ):
        study_id = get(row, CONCEPT.STUDY.ID)
        institution = get(row, CONCEPT.INVESTIGATOR.INSTITUTION)
        investigator_name = get(row, CONCEPT.INVESTIGATOR.NAME)
        study_name = get(row, CONCEPT.STUDY.NAME)
        attribution = get(row, CONCEPT.STUDY.ATTRIBUTION)
        short_name = get(row, CONCEPT.STUDY.SHORT_NAME)

        if not all((study_id, institution, investigator_name, study_name)):
            continue

        retval = {
            "resourceType": RESOURCE_TYPE,
            "id": make_identifier(RESOURCE_TYPE, study_id),
            "meta": {
                "profile": [
                    "http://fhir.kids-first.io/StructureDefinition/kfdrc-research-study"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kf-strides.org/studies",
                    "value": target_service_id,
                },
                {
                    "system": "https://kf-api-dataservice.kf-strides.org/studies?external_id=",
                    "value": study_id,
                },
            ],
            "extension": [
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/related-organization",
                    "extension": [
                        {
                            "url": "organization",
                            "valueReference": {
                                "reference": f'Organization/{organizations[institution]["id"]}'
                            },
                        }
                    ],
                }
            ],
            "title": study_name,
            "status": "completed",
            "principalInvestigator": {
                "reference": f'PractitionerRole/{practitioner_roles[(institution, investigator_name)]["id"]}'
            },
        }

        if attribution:
            retval["identifier"].append({"value": attribution})

        if short_name:
            retval["extension"].append(
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/display-name",
                    "valueString": short_name,
                }
            )

        if groups:
            retval["enrollment"] = [
                {"reference": f'Group/{group["id"]}'}
                for group in groups.values()
            ]

        yield retval
