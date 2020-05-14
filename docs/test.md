
# Integration Tests

This document describes the necessary additional testing that needs to be
executed on every pushed commit to Github.

## FHIR Model
Right now the Kids First FHIR model is unit tested by running the HL7 FHIR
IG Publisher which validates the conformance resources against the FHIR
specification and tests that example resources conform to the FHIR model in
the expected way.

However, these tests lack a couple of key things that are important to test and
can only be tested using the target FHIR server in which the FHIR model will
be loaded:

- **SearchParameters** - right now there is no test to ensure that a
  `SearchParameter` will work in a search query to the FHIR server in
   production.
- **FHIR model deployment** - there is no guarantee that the FHIR model will
  successfully deploy to the FHIR server in production.

We need to add integration tests that will test both of these things.

## FHIR Ingest

The Kids First team will use the `kf-lib-data-ingest` library to transform
and load source data into the Kids First FHIR server. This requires the
development of a FHIR service ingest plugin which consists of Python classes
responsible for transforming tabular source data into FHIR resources
that conform to the FHIR model.

Since the Python classes in the FHIR service ingest plugin are closely coupled
with the FHIR model, they should be developed, tested, and released alongside
the FHIR model.

We need to add integration tests that will ensure the FHIR service ingest
plugin successfully and correctly loads data into a FHIR server.

In this way we can ensure that the FHIR service ingest plugin
in a release of `kf-model-fhir` will work (with minimal bugs) in production.

## Data Migration

There will be times when a FHIR model deployment will make existing data
in the FHIR server non-conformant due to changes in the new model (e.g.
a previously null field becomes required).

When this scenario arises we will need to run a data migration on existing
data in the FHIR server before deploying the FHIR model. Data migrations should
be tested before they are run on production data so that we can reduce the
chances of failure.

TBD - this needs more thought bc its complicated ...

## Infrastructure

Ideally we can use CircleCI to run integration tests. However, the free version
of CircleCI has certain limitations (e.g. 10 min per step, compute resources)
that may cause us to consider another solution like Jenkins. CircleCI is ideal
because it can be used by others that want to fork the repository and the only
setup required is modifying the CircleCI YAML configuration.

No matter which CI solution is used, we will run the Kids First FHIR
server in a Docker Compose stack. The CI pipeline will spin up a fresh stack
for each pushed commit.

The only potential issue with this is the amount of time (~8 min) it takes to
initialize the Smile CDR database with the necessary tables and populate them
with the FHIR base model. This might make development very tedious.

Potential solutions for this are:

- Run Smile CDR with the in-memory H2 database instead of Postgres
- Use a snapshot of the Smile CDR Postgres database which already has all
  of the tables populated.

Both options should be explored.

## Implementation

### Tests

1. FHIR Model
    - Load the FHIR model into the test FHIR server

3. FHIR Ingest
    - Run the Kids First ingest pipeline with the FHIR service ingest plugin
      to load test data into the test FHIR server
    - Test that the FHIR resources in the server match our expectations
    - Minimum testing would be a simple count test for each resource type

4. `SearchParameter`s
    - Run search queries that make use of the `SearchParameter`s we loaded
      and ensure we get back expected results

### Data
Test data for integration tests will consist of tabular files that follow
the format of the Kids First Ingest Library transform stage output since
it will be loaded into the server using the FHIR service ingest plugin.

### Trigger
Integration tests should run on every pushed commit (similar to unit tests)

### Framework/Tools
We already use `pytest` for running unit tests and it works fairly well.
Integration tests aren't much different from unit tests except that they
interact with the FHIR server. We should `pytest` framework to define and
execute the integration tests as well.

We already use the `ncpi-fhir-utility` to validate the FHIR model. We can also
use it in the integration tests because it has functionality to interact with
the FHIR server (e.g. load the model, send HTTP requests).

### Standard Tests

#### FHIR Ingest
Every non-extension StructureDefinition (e.g.`kfdrc-patient`) will have a
Python mapper class in the FHIR service ingest plugin. The test for each
mapper class will follow a similar recipe:

- Convert a row in the source data to an instance of <resource type> conforming
  to the `Foo` profile.
- Load instance(s) of `Foo` into the FHIR server
- Query the server and check that the returned total count matches expected
  count

It would be nice to make it easy to add a test for a new mapper class. The
developer should only have to provide the path (or file name?) to the mapper
class and an expected count and the necessary integration tests for
the mapper should run.

This can be achieved fairly easily with pytest test parameterization.

#### SearchParameter
Similarly, adding a test for a `SearchParameter` should also be very easy. The
developer should only have to provide a path to the `SearchParameter` file and
an expected count.
