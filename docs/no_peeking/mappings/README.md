# Concept-Mappers between Kids First and Phenopackets FHIR

This directory curates Python modules mapping Kids First concepts to FHIR profiles against the [Phenopackets specifications](https://aehrc.github.io/fhir-phenopackets-ig/index.html).  
The following table shows conceptual mappings among KF entities, and Phenopackets and FHIR profiles:

| Kids First            | Phenopackets        | FHIR                  |
|-----------------------|---------------------|-----------------------|
| `family`              | `Family`            | `Group`               |
| `participant`         | `Individual`        | `Patient`             |
| `family_relationship` | `PedigreeNode`      | `FamilyMemberHistory` |
| `diagnosis`           | `Disease`           | `Condition`           |
| `phenotype`           | `PhenotypicFeature` | `Observation`         |
| `biospecimen`         | `Biosample`         | `Specimen`            |
| `genomic_file`        | `HtsFile`           | `DocumentReference`   |

As an initial pass, we created modules for the following profiles:

- `Family`;
- `Individual`;
- `PedigreeNode`;
- `Disease`;
- `PhenotypicFeature`; and
- `Biosample`

In creating the modules, the following attributes were considered:

- Most of the Phenopackets atrributes from the differential tables if mapped; and
- All the FHIR attributes required (based on cardinality) as well as `'id'` and `'identifier'`
