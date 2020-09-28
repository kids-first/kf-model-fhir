"""
Builds FHIR Task resources (https://www.hl7.org/fhir/Task.html)
from rows of tabular sequencing experiment data.
"""
import json

from kf_lib_data_ingest.common.concept_schema import CONCEPT

from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_sequencing_center import (
    SequencingCenter,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_specimen import (
    Specimen,
)
from kf_model_fhir.ingest_plugin.target_api_builders.kfdrc_genomic_file import (
    GenomicFile,
)
from kf_model_fhir.ingest_plugin.target_api_builders.sequencing_observation import (
    SequencingObservation,
)
from kf_model_fhir.ingest_plugin.shared import join


class SequencingTask:
    class_name = "sequencing_task"
    resource_type = "Task"
    target_id_concept = CONCEPT.SEQUENCING.TARGET_SERVICE_ID

    @staticmethod
    def build_key(record):
        assert None is not record[CONCEPT.SEQUENCING.ID]
        return record.get(CONCEPT.SEQUENCING.UNIQUE_KEY) or join(
            record[CONCEPT.SEQUENCING.ID]
        )
        
    @staticmethod
    def build_entity(record, key, get_target_id_from_record):
        study_id = record[CONCEPT.STUDY.ID]
        sequencing_id = record.get(CONCEPT.SEQUENCING.ID)
        sequencing_center = record.get(CONCEPT.SEQUENCING.CENTER.TARGET_SERVICE_ID)
        biospecimen_id = record.get(CONCEPT.BIOSPECIMEN.ID)
        sequencing_date = record.get(CONCEPT.SEQUENCING.DATE)
        instrument = record.get(CONCEPT.SEQUENCING.INSTRUMENT)
        library_name = record.get(CONCEPT.SEQUENCING.LIBRARY_NAME)
        library_strand = record.get(CONCEPT.SEQUENCING.LIBRARY_STRAND)
        paired_end = record.get(CONCEPT.SEQUENCING.PAIRED_END)
        platform = record.get(CONCEPT.SEQUENCING.PLATFORM)
        strategy = record.get(CONCEPT.SEQUENCING.STRATEGY)
        genomic_file_id = record.get(CONCEPT.GENOMIC_FILE.ID)
        sequencing_observation_id = (
            get_target_id_from_record(SequencingObservation, record)
        )

        entity = {
            "resourceType": SequencingTask.resource_type,
            "id": get_target_id_from_record(SequencingTask, record),
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/StructureDefinition/Task"
                ]
            },
            "identifier": [
                {
                    "system": "https://kf-api-dataservice.kidsfirstdrc.org/sequencing-experiments?external_id=",
                    "value": sequencing_id,
                },
                {
                    "system": "urn:kids-first:unique-string",
                    "value": join(SequencingTask.resource_type, study_id, key),
                },
            ],
            "status": "completed",
            "intent": "order",
        }

        if sequencing_date:
            entity["authoredOn"] = sequencing_date
        
        if sequencing_center:
            entity["owner"] = {
                "reference": f"Organization/{get_target_id_from_record(SequencingCenter, record)}"
            }
         
        input_list = []

        if biospecimen_id:
            input_list.append(
                {
                    "type": {"text": "biospecimen"},
                    "valueReference": {
                        "reference": f"Specimen/{get_target_id_from_record(Specimen, record)}"
                    },
                }
            )

        if instrument:
            input_list.append(
                {
                    "type": {"text": "instrument"},
                    "valueCodeableConcept": {"text": instrument},
                }
            )

        if library_name:
            input_list.append(
                {
                    "type": {"text": "library_name"},
                    "valueCodeableConcept": {"text": library_name},
                }
            ) 

        if library_strand:
            input_list.append(
                {
                    "type": {"text": "library_strand"},
                    "valueCodeableConcept": {"text": library_strand},
                }
            )

        if paired_end:
            input_list.append(
                {
                    "type": {"text": "paired_end"},
                    "valueBoolean": json.loads(paired_end.lower()),
                }
            )

        if platform:
            input_list.append(
                {
                    "type": {"text": "platform"},
                    "valueCodeableConcept": {"text": platform},
                }
            )

        if strategy:
            input_list.append(
                {
                    "type": {"text": "experiment_strategy"},
                    "valueCodeableConcept": {"text": strategy},
                }
            )

        if input_list:
            entity["input"] = input_list

        output = []
        
        if genomic_file_id:
            output.append( 
                {
                    "type": {"text": "genomic_file"},
                    "valueReference": {
                        "reference": f"DocumentReference/{get_target_id_from_record(GenomicFile, record)}"
                    },
                } 
            )
            
        if sequencing_observation_id:
            output.append(
                {
                    "type": {"text": "sequencing_experiment"},
                    "valueReference": {
                        "reference": f"Observation/{sequencing_observation_id}"
                    },
                }
            )

        if output:
            entity["output"] = output

        return entity
