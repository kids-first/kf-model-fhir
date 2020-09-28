"""
Builds FHIR Observation resources (https://www.hl7.org/fhir/observation.html)
from rows of tabular sequencing experiment data.
"""
import json

from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_genomic_file import (
    GenomicFile,
)
from kf_model_fhir.ingest_plugin.shared import join

class SequencingObservation:
    class_name = "sequencing_observation"
    resource_type = "Observation"
    target_id_concept = None

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.SEQUENCING.ID]
        assert False is not any(
            [
                record.get(CONCEPT.SEQUENCING.MAX_INSERT_SIZE),
                record.get(CONCEPT.SEQUENCING.MEAN_DEPTH),
                record.get(CONCEPT.SEQUENCING.MEAN_INSERT_SIZE),
                record.get(CONCEPT.SEQUENCING.MEAN_READ_LENGTH),
                record.get(CONCEPT.SEQUENCING.TOTAL_READS),
                record.get(CONCEPT.GENOMIC_FILE.HARMONIZED),
                record.get(CONCEPT.GENOMIC_FILE.REFERENCE_GENOME),
            ]
        )
        return record.get(CONCEPT.SEQUENCING.UNIQUE_KEY) or join(
            record[CONCEPT.SEQUENCING.ID]
        )
        
    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        sequencing_id = record.get(CONCEPT.SEQUENCING.ID)
        genomic_file_id = record.get(CONCEPT.GENOMIC_FILE.ID)
        max_insert_size = record.get(CONCEPT.SEQUENCING.MAX_INSERT_SIZE)
        mean_depth = record.get(CONCEPT.SEQUENCING.MEAN_DEPTH)
        mean_insert_size = record.get(CONCEPT.SEQUENCING.MEAN_INSERT_SIZE)
        mean_read_length = record.get(CONCEPT.SEQUENCING.MEAN_READ_LENGTH)
        total_reads = record.get(CONCEPT.SEQUENCING.TOTAL_READS)
        harmonized = record.get(CONCEPT.GENOMIC_FILE.HARMONIZED)
        reference_genome = record.get(CONCEPT.GENOMIC_FILE.REFERENCE_GENOME)
        
        entity = {
            "resourceType": SequencingObservation.resource_type,
            "id": get_target_id_from_record(SequencingObservation, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Observation"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-experiments?external_id=",
                    "value": sequencing_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(SequencingObservation.resource_type, study_id, key),
                },
            ],
            "status": "final",
            "code": {
                "text": "sequencing_experiment",
            },
        }
        
        if genomic_file_id:
            entity.setdefault("focus", []).append(
                {
                    "reference": f"DocumentReference/{get_target_id_from_record(GenomicFile, record)}"
                }
            )

        component = []

        if max_insert_size:
            component.append(
                {
                    "code": {"text": "max_insert_size"},
                    "valueQuantity": {"value": int(max_insert_size)},
                }
            )
        
        if mean_depth:
            component.append(
                {
                    "code": {"text": "mean_depth"},
                    "valueQuantity": {"value": float(mean_depth)},
                }
            )  
            
        if mean_insert_size:
            component.append(
                {
                    "code": {"text": "mean_insert_size"},
                    "valueQuantity": {"value": float(mean_insert_size)},
                }
            ) 
            
        if mean_read_length:
            component.append(
                {
                    "code": {"text": "mean_read_length"},
                    "valueQuantity": {"value": float(mean_read_length)},
                }
            ) 

        if total_reads:
            component.append(
                {
                    "code": {"text": "total_reads"},
                    "valueQuantity": {"value": int(total_reads)},
                }
            ) 
            
        if harmonized:
            component.append(
                {
                    "code": {"text": "is_harmonized"},
                    "valueBoolean": json.loads(harmonized.lower()),
                }
            ) 
            
        if reference_genome:
            component.append(
                {
                    "code": {"text": "reference_genome"},
                    "valueCodeableConcept": {"text": reference_genome},
                }
            ) 

        if component:
            entity["component"] = component

        return entity
