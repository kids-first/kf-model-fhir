# Python Ingest Plugin for FHIR ETL

This directory curates the Python ingest plugin for [kf-lib-data-ingest](https://github.com/kids-first/kf-lib-data-ingest/) converting Kids First data to Kids First DRC FHIR resources.
The following table shows conceptual mappings among KF entities, FHIR profiles, and KF DRC FHIR profiles:

| Kids First | FHIR | Kids First DRC FHIR |
|--|--|--|
| `investigator` | `Practitioner` <br> `Organization` <br> `PractitionerRole` | Not applicable |
| `study` | `ResearchStudy` | `kfdrc-research-study` |
| `participant` | `Patient` <br> `ResearchSubject` | `kfdrc-patient` <br> Not applicable |
| `family` | `Group` | Not applicable |
| `family_relationship` | Not applicable | `kfdrc-patient.relation` |
| `diagnosis` | `Condition` | `kfdrc-condition` |
| `phenotype` | `Observation` | `kfdrc-phenotype` |
| `outcome` | `Observation` | `kfdrc-vital-status` |
| `biospecimen` | `Specimen` | `kfdrc-specimen` |
| `sequencing_center` | `Organization` | Not applicable |

Our mapping effort in progress is documented at [KF DRC FHIR Model Mappings](https://docs.google.com/spreadsheets/d/19tQnE75UzvP_k29D-QprbsJ-6ZO2PdUmKPiWHKkcTEg/edit#gid=1197884015).
