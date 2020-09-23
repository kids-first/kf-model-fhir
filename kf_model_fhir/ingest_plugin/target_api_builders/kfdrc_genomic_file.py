"""
Builds FHIR DocumentReference resources (http://hl7.org/fhir/R4/documentreference.html) 
from rows of tabular genomic file data.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT
from kf_lib_data_ingest.common.misc import str_to_obj

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_patient import (
    Patient,
)
from kf_model_fhir.ingest_plugin.shared import join

# http://fhir.kids-first.io/ValueSet/data-type
data_type_dict = {
    constants.GENOMIC_FILE.DATA_TYPE.ALIGNED_READS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C164052",
                "display": "Aligned Sequence Read",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.ALIGNED_READS,
    },
    constants.GENOMIC_FILE.DATA_TYPE.GENE_EXPRESSION: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C16608",
                "display": "Gene Expression",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.GENE_EXPRESSION,
    },
    constants.GENOMIC_FILE.DATA_TYPE.GENE_FUSIONS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C20195",
                "display": "Gene Fusion",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.GENE_FUSIONS,
    },
    constants.GENOMIC_FILE.DATA_TYPE.OPERATION_REPORTS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C114420",
                "display": "Operative Report",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.OPERATION_REPORTS,
    },
    constants.GENOMIC_FILE.DATA_TYPE.PATHOLOGY_REPORTS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C28277",
                "display": "Pathology Report",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.PATHOLOGY_REPORTS,
    },
    constants.GENOMIC_FILE.DATA_TYPE.ANNOTATED_SOMATIC_MUTATIONS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C18060",
                "display": "Somatic Mutation",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.ANNOTATED_SOMATIC_MUTATIONS,
    },
    constants.GENOMIC_FILE.DATA_TYPE.UNALIGNED_READS: {
        "coding": [
            {
                "system": "http://fhir.kids-first.io/CodeSystem/data-type",
                "code": "C164053",
                "display": "Unaligned Sequence Read",
            }
        ],
        "text": constants.GENOMIC_FILE.DATA_TYPE.UNALIGNED_READS,
    },
}


class GenomicFile:
    class_name = "genomic_file"
    resource_type = "DocumentReference"
    target_id_concept = CONCEPT.GENOMIC_FILE.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.GENOMIC_FILE.ID]
        return record.get(CONCEPT.GENOMIC_FILE.UNIQUE_KEY) or join(
            record[CONCEPT.GENOMIC_FILE.ID]
        )

    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        genomic_file_id = record.get(CONCEPT.GENOMIC_FILE.ID)
        acl = str_to_obj(record.get(CONCEPT.GENOMIC_FILE.ACL))
        data_type = record.get(CONCEPT.GENOMIC_FILE.DATA_TYPE)
        participant_id = record.get(CONCEPT.PARTICIPANT.ID)
        size = int(record.get(CONCEPT.GENOMIC_FILE.SIZE))
        url_list = str_to_obj(record.get(CONCEPT.GENOMIC_FILE.URL_LIST))
        file_name = record.get(CONCEPT.GENOMIC_FILE.FILE_NAME)
        file_format = record.get(CONCEPT.GENOMIC_FILE.FILE_FORMAT)

        entity = {
            "resourceType": GenomicFile.resource_type,
            "id": get_target_id_from_record(GenomicFile, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/DocumentReference"
                ]
            },
            "identifier": [
                {
                    "system": f"https://kf-api-dataservice.kidsfirstdrc.org/genomic-files?study_id={study_id}&external_id=",
                    "value": genomic_file_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(GenomicFile.resource_type, study_id, key),
                },
            ],
            "status": "current",
        }

        if acl:
            entity.setdefault("extension", []).append(
                {
                    "extension": [
                        {
                            "url": "file-accession",
                            "valueIdentifier": {
                                "value": accession
                            },
                        }
                        for accession in acl
                    ],
                    "url": "http://fhir.kids-first.io/StructureDefinition/accession-identifier",
                }
            )

        if data_type:
            if data_type_dict.get(data_type):
                entity["type"] = data_type_dict[data_type]
            else:
                entity.setdefault('type', {})['text'] = data_type

        if participant_id:
            entity["subject"] = {
                "reference": f"Patient/{get_target_id_from_record(Patient, record)}"
            }

        content = {}

        if size:
            content.setdefault('attachment', {})["extension"] = [
                {
                    "url": "http://fhir.kids-first.io/StructureDefinition/large-size",
                    "valueDecimal": size,
                }
            ]

        if url_list:
            content.setdefault('attachment', {})["url"] = url_list[0]

        if file_name:
            content.setdefault('attachment', {})["title"] = file_name

        if file_format:
            content["format"] = {
                "display": file_format
            }

        if content:
            entity.setdefault("content", []).append(content)
    
        return entity
