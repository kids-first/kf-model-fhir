# Python Modules for FHIR ETL

This directory curates Python modules converting Kids First data to Kids First DRC FHIR resources.
The following table shows conceptual mappings among KF entities, FHIR profiles, and KF DRC FHIR profiles:

| Kids First             | FHIR                   | Kids First DRC FHIR    |
|------------------------|------------------------|------------------------|
| `participant`          | `Patient`              | `kfdrc-patient`        |
| `diagnosis`            | `Condition`            | `kfdrc-condition`      |
| `phenotype`            | `Observation`          | `kfdrc-phenotype`      |
| `biospecimen`          | `Specimen`             | `kfdrc-specimen`       |

Our mapping effort in progress is documented at [KF DRC FHIR Model Mappings](https://docs.google.com/spreadsheets/d/19tQnE75UzvP_k29D-QprbsJ-6ZO2PdUmKPiWHKkcTEg/edit#gid=1197884015).
