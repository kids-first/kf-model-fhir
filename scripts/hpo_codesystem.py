#!/usr/bin/env python

import json
import os
import sys

# OWL to FHIR transformer compiled from https://github.com/aehrc/fhir-owl
FHIR_OWL_BIN = "fhir-owl-1.1.0-SNAPSHOT.jar"

# Convert OWL file to FHIR CodeSystem
ret = os.system(f'wget -N http://purl.obolibrary.org/obo/hp.owl && java -jar {FHIR_OWL_BIN} -i hp.owl -o hpo_codesystem.json -id hpo -name "Human Phenotype Ontology" -content not-present -mainNs http://purl.obolibrary.org/obo/HP_ -descriptionProp http://purl.org/dc/elements/1.1/subject -status active -codeReplace _,:')

if ret != 0:
    sys.exit()

# Remove cross-references to other ontologies

with open("hpo_codesystem.json") as hj:
    hpo = json.load(hj)

hpo["concept"] = [c for c in hpo["concept"] if c["code"].startswith("HP:")]
for c in hpo["concept"]:
    c.pop("designation", None)

with open("hpo_codesystem.json", "w") as hj:
    json.dump(hpo, hj)
