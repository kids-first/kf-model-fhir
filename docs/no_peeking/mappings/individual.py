"""
This module maps Kids First participant to Phenopackets Individual (derived from FHIR Patient).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Individual.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

from .shared import get, codeable_concept, make_identifier, make_select, GO_AWAY_SERVER

# http://ga4gh.org/fhir/phenopackets/CodeSystem/karyotypic-sex
karyotypic_sex_coding = {
    constants.GENDER.FEMALE: {
        "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex",
        "code": "XX",
        "display": "Female",
    },
    constants.GENDER.MALE: {
        "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex",
        "code": "XY",
        "display": "Male",
    },
    constants.COMMON.OTHER: {
        "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex",
        "code": "OTHER_KARYOTYPE",
        "display": "None of the above types",
    },
    constants.COMMON.UNKNOWN: {
        "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex",
        "code": "UNKNOWN_KARYOTYPE",
        "display": "Untyped or inconclusive karyotyping",
    },
}

# http://purl.obolibrary.org/obo/ncbitaxon.owl
ncbitaxon_coding = {
    constants.SPECIES.DOG: {
        "system": "http://purl.obolibrary.org/obo/ncbitaxon.owl",
        "code": "NCBITaxon:9615",
        "display": "Canis lupus familiaris",
    },
    constants.SPECIES.HUMAN: {
        "system": "http://purl.obolibrary.org/obo/ncbitaxon.owl",
        "code": "NCBITaxon:9606",
        "display": "Homo sapiens",
    },
}

# http://hl7.org/fhir/R4/valueset-administrative-gender.html
administrative_gender = {
    constants.GENDER.FEMALE: "female",
    constants.GENDER.MALE: "male",
    constants.COMMON.OTHER: "other",
    constants.COMMON.UNKNOWN: "unknown",
}

resource_type = "Patient"


def yield_individuals(eng, table, study_id):
    for row in make_select(eng, table, CONCEPT.PARTICIPANT.ID, CONCEPT.PARTICIPANT.SPECIES, CONCEPT.PARTICIPANT.GENDER):
        id = get(row, CONCEPT.PARTICIPANT.ID)
        species = get(row, CONCEPT.PARTICIPANT.SPECIES) or constants.SPECIES.HUMAN
        gender = get(row, CONCEPT.PARTICIPANT.GENDER) or constants.COMMON.UNKNOWN

        if not id:
            continue

        retval = {
            "resourceType": resource_type,
            "text": {
                "status": "empty",
                "div": GO_AWAY_SERVER
            },
            "id": make_identifier(resource_type, study_id, id),
            "meta": {
                "profile": ["http://ga4gh.org/fhir/phenopackets/StructureDefinition/Individual"]
            },
            "identifier": [{"system": f"http://kf-api-dataservice.kidsfirstdrc.org/participants?study_id={study_id}", "value": id}],
        }

        if gender:
            retval.setdefault("extension", []).append(
                {
                    "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/KaryotypicSex",
                    "valueCodeableConcept": codeable_concept(gender, [karyotypic_sex_coding], "karyotypic sex"),
                }
            )
            retval["gender"] = administrative_gender[gender]

        # if species:
        #     retval.setdefault("extension", []).append(
        #         {
        #             "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Taxonomy",
        #             "valueCodeableConcept": codeable_concept(species, [ncbitaxon_coding], "taxonomy"),
        #         }
        #     )

        yield retval, id
