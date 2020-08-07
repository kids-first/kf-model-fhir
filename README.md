<p align="center">
  <img src="docs/images/logo.svg" alt="Kids First FHIR Data Model" width="660px">
</p>
<p align="center">
  <a href="https://github.com/kids-first/kf-model-fhir/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kids-first/kf-model-fhir.svg?style=for-the-badge"></a>
  <a href="https://circleci.com/gh/kids-first/kf-model-fhir"><img src="https://img.shields.io/circleci/project/github/kids-first/kf-model-fhir.svg?style=for-the-badge"></a>
</p>

# 🔥 Kids First FHIR Data Model

This is an experimental repository for developing the Kids First
FHIR data model for FHIR version R4.

## Overview

This repository contains:

1. [Kids First FHIR ImplementationGuide](site_root) - the files and required
folder structure needed build HL7 documentation (known as an ImplementationGuide)
for the FHIR data model
2. [Kids First FHIR Data Model](site_root/input/resources) - conformance and
example resource files that make up the FHIR model.
3. [Kids First FHIR Service Ingest Plugin](kf_model_fhir/ingest_plugin) - for
transforming source data into FHIR resources that conform to the Kids First
FHIR model using the [Kids First Data Ingest Library](https://github.com/kids-first/kf-lib-data-ingest)
4. [Integration Tests](tests) - to test things that require a FHIR server
(e.g. model deployment, FHIR ingest, search parameters)

## FHIR 101 - A Practical Guide

If you have never heard of FHIR, are unfamiliar with how to implement FHIR,
or are confused by any of the terms in this README, then
checkout the [FHIR 101 Jupyter Notebook](https://github.com/fhir-sci/fhir-101).

## Installation

### Prerequisite

Make sure you have Docker CE installed: <https://docs.docker.com/install/>

Docker is needed because it is used by both the `fhirutil` CLI and the
integration tests.

1. Git clone this repository

    ```shell
    git clone git@github.com:kids-first/kf-model-fhir.git
    cd kf-model-fhir
    ```

2. Setup a Python virtual environment (optional, but recommended)

    ```shell
    python3 -m venv venv
    source ./venv/bin/activate
    ```

3. Install the necessary requirements

    ```shell
    pip install -e .
    ```

## FHIR Model Development

You can use any tool (Forge, cimpl, etc.) to develop your FHIR resources
but for example purposes we will simple copy existing resources into the
FHIR model.

Follow the steps below to get an idea of how FHIR model development and
validation works.

### 1. Add a new conformance resource

```shell
cp docs/data/StructureDefinition-research-study.json site_root/input/resources/profiles
```

### 2. Add a new example resource to test the conformance resource

```shell
cp docs/data/ResearchStudy-sd-001.json site_root/input/resources/examples
```

### 3. Validate the model

There are two ways to use the `fhirutil` CLI to validate the model.

```shell
# Method 1 - Uses the Dockerized IG publisher
fhirutil validate ./site_root/ig.ini --publisher_opts='-tx n/a'

# Method 2 - Uses native IG publisher - faster than above method
fhirutil add ./site_root/input/resources
java -jar org.hl7.fhir.publisher.jar -ig site_root/ig.ini -tx n/a
```

Method 2 is faster since it's running the IG Publisher directly and does
not need to spin up a Docker container, but it means that you must first
install the IG Publisher yourself ([IG Publisher installation instructions](https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation#IGPublisherDocumentation-Installing)).

See [NCPI FHIR Utility](https://github.com/ncpi-fhir/ncpi-fhir-utility)
for more information on these two methods.

### 4. View Validation Results

The CLI will log output to the screen and tell you whether
validation succeeded or failed. You can view detailed validation
results at `./site_root/output/qa.html`

## FHIR Ingest Development

As mentioned before, this repository contains both the FHIR model and a
Python package to transform source data into FHIR resources and load them
into a FHIR server.

This Python package is known as a FHIR Ingest Plugin and it conforms to the
Kids First Data Ingest Library's target service plugin architecture.

### 1. Develop the FHIR Ingest Plugin

Detailed information about making target service plugins can be found in the
Kids First Data Ingest Library documentation at:<br>
https://kids-first.github.io/kf-lib-data-ingest/tutorial/target_service_plugins/how_to_make.html

### 2. (Optional) Update the [test data file](tests/data/study_df.tsv)

If needed, add necessary columns and rows to the test data file with data
needed to build instances of the FHIR resource. The test data file already
includes everything it needs to build Kids First Patient resources.

### 3. Test the FHIR Ingest Plugin

**NOTE** - In order to run the integration tests, you must have access
to the `kidsfirstdrc/smilecdr:test` Docker image on DockerHub. Also,
ensure your DockerHub credentials are set in your environment
(`DOCKER_HUB_USERNAME`, `DOCKER_HUB_PW`).

This runs all of the integration tests which include tests for the FHIR
ingest plugin:

```shell
./scripts/integration_test.sh
```

See [Integration Tests](#Integration-Tests) for development details.

### Version Control

Similar to other Kids First code repository, this repository will use Git flow
for collaborative code development and version control.  Please review
the [Kids First Developer Handbook](https://kids-first.github.io/kf-developer-handbook/development/feature_lifecycle.html) if you are not familiar with this.

### Repository Layout

- Source files for FHIR Model ImplementationGuide (IG): `site_root`
- Source code for FHIR Ingest Plugin: `kf_model_fhir`
- Integration tests: `tests`

```text
site_root
├── ig.ini                                     -> IG configuration file
├── input
│   ├── ImplementationGuide-KidsFirst.json     -> IG FHIR resource
│   └── resources                              -> FHIR resources that make up the models
│       ├── examples                           -> Example resources
│       ├── extensions                         -> Extensions
│       ├── profiles                           -> StructureDefinition (non-Extension)
│       ├── search                             -> SearchParameters
│       └── terminology                        -> CodeSystems, ValueSets
```

The files `ig.ini` and `ImplementationGuide-KidsFirst.json` contain
configuration information for the FHIR model's ImplementationGuide and
affect which resources are validated and included in the generated site.

Read more about them [here](https://build.fhir.org/ig/FHIR/ig-guidance/index.html)
and [here](http://www.hl7.org/fhir/implementationguide.html)

### Naming Conventions

Since the Kids First FHIR model is validated using the `ncpi-fhir-utility`,
the FHIR resource payloads and filenames are expected to follow certain
standards otherwise validation will fail.  

Please see the NCPI FHIR Utility's
[naming conventions doc](https://github.com/ncpi-fhir/ncpi-fhir-utility/blob/master/docs/naming_conventions.md) for details.

## Testing

### Unit Tests

The unit test for the FHIR model is the same as the
[Validate the Model](#3-validate-the-model) step
in FHIR Model Development section. The unit test is automatically run by the
repository's [CI pipeline](.circleci/config.yml).

### Integration Tests

There are some things that cannot be tested without a FHIR server. These
include deploying the FHIR model to the server, using the FHIR Ingest Plugin,
and using SearchParameters. Integration tests are also automatically run by
the repository's CI pipeline.

#### Test Runner

Integration tests are run using the script `scripts/integration_test.sh`. This
script spins up an test instance of the [Kids First FHIR Service](https://github.com/kids-first/kf-api-fhir-service) if one is not already running. Then it uses `pytest` to execute
the tests in the `tests` directory.

#### Tests

Here is an overview of the test directory:

```text
tests
├── conftest.py          -> Includes test setup and shared test fixtures
├── data                 -> Test data
│   └── study_df.tsv  
└── test_app.py          -> Integration test definitions
```  

So far the integration tests in `test_app.py` include:

**1. Model Deploy Test**

Submits resources in the FHIR model to the test server and ensures there
were no errors.

A developer should never have to modify this test since the test is setup
to deploy all resources in the FHIR model to the FHIR server.

**2. FHIR Ingest Plugin Tests**

These tests run the Kids First FHIR Ingest Plugin to ingest the test
data table into the test FHIR server. See
`tests/conftest.py::load_fhir_resources`.

Then, for each specified resource type in the test parameter input list,
it queries the server for that resource type and checks that the total
equals the expected count. See `tests/test_app.py::test_ingest_plugin`.

Each time a new Target Entity Builder is added to the FHIR Ingest Plugin,
new test parameters (resource_type and expected count) must be added
to the ingest plugin's test parameter list:

```python
@pytest.mark.parametrize(
    "resource_type,expected_count",
    [
        ('Patient', 10),
        # Add additional tuples of the form: (resource_type, expected_count)
    ]
)
def test_ingest_plugin(client, load_fhir_resources, resource_type, expected_count)
```

**3. Search Parameter Tests**

Run a search query that using a SearchParameter in the FHIR model
and ensure the returned resource total equals the expected count.

**NOTE** - These tests are defined but are not currently run due to
this unresolved [issue](https://github.com/kids-first/kf-api-fhir-service/issues/81)
with the FHIR server.
