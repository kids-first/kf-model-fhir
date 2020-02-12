

def species_id(label):
    if label==constants.SPECIES.HUMAN:
        return "NCBITaxon:9606"
    elif label == constants.SPECIES.DOG:
        return "NCBITaxon:9615"
    else:
        raise Exception("Unknown species identifier")

def phenotype_id(label):
    #hpo lookup for label
    pass

def tissue_id(label):
    pass


phenopacket {
    "id": NEW_KIND_OF_KFID?,
    "subject: {
        "id": PARTICIPANT.ID,
        "alternate_ids": None,
        "date_of_birth": None,       # delete this from record
        "age": "P" + PARTICIPANT.ENROLLMENT_AGE_DAYS + "D",   # https://en.wikipedia.org/wiki/ISO_8601#Durations
        "sex": PARTICIPANT.GENDER,
        "karyotypic_sex": None,
        "taxonomy": {
            "id": species_id(PARTICIPANT.SPECIES or constants.SPECIES.HUMAN),
            "label": PARTICIPANT.SPECIES or constants.SPECIES.HUMAN
        }
    },
    "phenotypic_features": [
        {
            "type": {
                "id": phenotype_id(PHENOTYPE.NAME),
                "label": PHENOTYPE.NAME
            },
            "negated": not PHENOTYPE.OBSERVED
        }, ...
    ],
    "biosamples":  [
        {
            "id": BIOSPECIMEN.ID,
            "individual_id": PARTICIPANT.ID,
            "sampled_tissue": {
                "id": tissue_id(BIOSPECIMEN.TISSUE_TYPE)
                "label": BIOSPECIMEN.TISSUE_TYPE
            },
            "phenotypic_features": [?],
            "taxonomy": PARTICIPANT.SPECIES,
            "individual_age_at_collection": BIOSPECIMEN.EVENT_AGE_DAYS or PARTICIPANT.ENROLLMENT_AGE_DAYS,
            "histological_diagnosis": None,
            "tumor_progression": None,
            "tumor_grade": None,
            "diagnostic_markers": None,
            "procedure": None,
            "hts_files": [
                {
                    "uri": GENOMIC_FILE.URL_LIST[0],    # Only one. This really need to be the Gen3 URL.
                    "description": None,
                    "htsFormat": GENOMIC_FILE.FILE_FORMAT,
                    "genomeAssembly": GENOMIC_FILE.REFERENCE_GENOME,
                    "individualToSampleIdentifiers": {
                        "patient23456": "NA12345"
                    }
                }, ...
            ],
        }
    ]
}
