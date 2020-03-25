# Phenopackets Feedback and Questions

## CodeSystem

- The coverage of Phenopackets' default CodeSystems (as well as FHIR's) is quite limited––e.g. Disease `'code'`, PhenotypicFeature `'code'`, Specimen `'type'` and `'collection'` `'method'`, etc.
- The selection criteria of the above included code systems are less clearly described or nebulous.

## PhenotypicFeature

- How does the validation of PhenotypicFeature CodeableConcept Extensions work? (`'Severity'`, `'PhenotypicFeatureModifier'`, `'code'`, etc.)
  - It is not easy to locate the above code systems elsewhere.
  - The use of listed concepts doesn't work.
    - For example, given [the value set of 2,000 concepts for code](https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-PhenotypicFeatureType.html), even the use of listed concepts returns an error when POSTing new resources.
  - Should we add a Phenopackets ontology ETL in order to fetch and keep any downstream server's CodeSystems up-to-date (if Phenopackets provides pre-built ontologies)?

## Disease

- How does the validation of Disease CodeableConcept extensions (`'CodedOnset'`, `'TumorStage'`, `'code'`, etc.) work?
  - It is not easy to locate the above code systems elsewhere.
  - The use of listed concepts doesn't work.
    - For example, given [the value set of 1,000 concepts for `'TumorStage'`](https://aehrc.github.io/fhir-phenopackets-ig/ValueSet-TumorStage.html), even the use of listed concepts returns an error when POSTing new resources.
  - As opposed to the validation of PhenotypicFeature's `'code'` above, the use of ontologies other than <http://hl7.org/fhir/R4/valueset-condition-code.html> doesn't return an error, but a warning.
- As opposed to PhenotypicFeature's reference to `'specimen'`, Disease doesn't have a linkage attribute to Specimen.
