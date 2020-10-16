"""
Builds FHIR ResearchSubject resources (https://www.hl7.org/fhir/researchsubject.html)
from rows of tabular participant data.
"""
# from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_model_fhir.ingest_plugin.shared import make_id, not_none, submit
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_research_study import (
    ResearchStudy,
)

# https://www.hl7.org/fhir/valueset-research-subject-status.html
research_subject_status = "off-study"


class ResearchSubject:
    class_name = "research_subject"
    resource_type = "ResearchSubject"
    # Patient already uses CONCEPT.PARTICIPANT.TARGET_SERVICE_ID,
    # so the below is set to None
    target_id_concept = None

    @classmethod
    def get_key_components(cls, record, get_target_id_from_record):
        study_id = not_none(record[CONCEPT.STUDY.TARGET_SERVICE_ID])
        participant_id = not_none(record[CONCEPT.PARTICIPANT.ID])
        return {
            "study": {
                "reference": f"{ResearchStudy.resource_type}/{make_id(study_id)}"
            },
            "individual": {
                "reference": f"{Patient.resource_type}/{get_target_id_from_record(Patient, record)}"
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/participants?",
                    "value": f"study_id={study_id}&external_id={participant_id}",
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
                    "http://hl7.org/fhir/StructureDefinition/ResearchSubject"
                ]
            },
            "status": research_subject_status,
        }

        return {
            **cls.get_key_components(record, get_target_id_from_record),
            **entity,
        }

    @classmethod
    def submit(cls, host, body):
        return submit(host, cls, body)
