"""
This module maps Kids First participant to Phenopackets Individual (derived from FHIR Patient).
Please visit https://aehrc.github.io/fhir-phenopackets-ig/StructureDefinition-Individual.html
    for the detailed structure definition.
"""
from kf_lib_data_ingest.common import constants
from kf_lib_data_ingest.common.concept_schema import CONCEPT

# http://ga4gh.org/fhir/phenopackets/CodeSystem/KaryotypicSex
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


def _list_codings(x, codings, name):
    results = [c[x] for c in codings if x in c]
    if not results:
        raise Exception(f"No {name} codings found for {x}")
    return results


def list_karyotypicsex_codings(x):
    return _list_codings(x, [karyotypic_sex_coding], "karyotypic sex")


def list_taxonomy_codings(x):
    return _list_codings(x, [ncbitaxon_coding], "taxonomy")


# http://hl7.org/fhir/R4/valueset-administrative-gender.html
administrative_gender = {
    constants.GENDER.FEMALE: "female",
    constants.GENDER.MALE: "male",
    constants.COMMON.OTHER: "other",
    constants.COMMON.UNKNOWN: "unknown",
}


def make_individual(row, study_id):
    if not row.get(CONCEPT.PARTICIPANT.ID):
        return None

    species = row.get(CONCEPT.PARTICIPANT.SPECIES) or constants.SPECIES.HUMAN
    gender = row.get(CONCEPT.PARTICIPANT.GENDER) or constants.COMMON.UNKNOWN
    return {
        "resourceType": "Patient",
        "id": row.get(CONCEPT.PARTICIPANT.TARGET_SERVICE_ID) or None,
        "meta": {
            "profile": [
                "http://ga4gh.fhir.phenopackets/StructureDefinition/Individual"
            ]
        },
        "extension": [
            {
                "text": "KaryotypicSex",
                "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/KaryotypicSex",
                "valueCodeableConcept": {
                    "coding": list_karyotypicsex_codings(gender),
                    "text": gender,
                },
            },
            {
                "text": "Taxonomy",
                "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Taxonomy",
                "valueCodeableConcept": {
                    "coding": list_taxonomy_codings(species),
                    "text": species,
                },
            },
        ],
        "identifier": [
            {
                "system": "https://kf-api-dataservice.kidsfirstdrc.org/participants",
                "value": row.get(CONCEPT.PARTICIPANT.TARGET_SERVICE_ID) or None,
            },
            {"system": study_id, "value": row[CONCEPT.PARTICIPANT.ID]},
        ],
        "gender": administrative_gender[gender],
    }
