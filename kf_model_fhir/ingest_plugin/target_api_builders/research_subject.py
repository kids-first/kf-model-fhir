"""
Builds FHIR ResearchSubject resources (https://www.hl7.org/fhir/researchsubject.html) 
from rows of tabular participant data.
"""
# from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_research_study import (
    ResearchStudy,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)

from kf_model_fhir.ingest_plugin.shared import join, make_safe_identifier

# https://www.hl7.org/fhir/valueset-research-subject-status.html
research_subject_status = "off-study"


class ResearchSubject:
    class_name = "research_subject"
    resource_type = "ResearchSubject"
    # Patient already uses CONCEPT.PARTICIPANT.TARGET_SERVICE_ID,
    # so the below is set to None
    target_id_concept = None

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.STUDY.ID]
        assert None is not record[CONCEPT.PARTICIPANT.ID]
        return join(
            record[CONCEPT.STUDY.ID],
            record[CONCEPT.PARTICIPANT.ID],
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        participant_id = record.get(CONCEPT.PARTICIPANT.ID)

        entity = {
            "resourceType": ResearchSubject.resource_type,
            "id": make_safe_identifier(
                get_target_id_from_record(ResearchSubject, record)
            ),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/ResearchSubject"
                ]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kidsfirstdrc.org/participants?study_id={study_id}&external_id=",
                    "value": participant_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(Patient.resource_type, study_id, key),
                },
            ],
            "status": research_subject_status,
            "study": {
                "reference": f"ResearchStudy/{make_safe_identifier(get_target_id_from_record(ResearchStudy, record))}"
            },
            "individual": {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            },
        }

        return entity
