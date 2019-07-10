# 🔥 Kids First FHIR Data Model

This is an experimental repository for developing the Kids First
FHIR data model for FHIR version STU3.

The repository uses the Firely technology stack: https://simplifier.net/downloads
to validate the model and provide a sample FHIR server to make use of the model
with real data.

## Background
FHIR is an HL7 data interoperability specification which includes a definition of
a base data model and a standard for a RESTful API to
interact with FHIR data that conforms to the model. See https://www.hl7.org/fhir/.

The base FHIR data model consists of a set of XML/JSON files that specify
FHIR entity (called a Resource) definitions, referential constraints between
Resources, and constraints on Resource attributes.

See https://www.hl7.org/fhir/downloads.html.

Most of these files contain FHIR StructureDefinition resources which specify
the definitions and constraints.

StructureDefinitions are very often called **"Profiles"** colloquially.
The term **"Resource"** often refers to non-StructureDefinitions FHIR resources
such as Patient, Specimen, etc.


### Model Development
To "develop" a FHIR data model means to:

1. **Create additional StructureDefinition file(s)**

    If you look at the base model, you'll notice that the constraints are very
    loose (almost nothing is required). This might not be ideal for real world
    use cases. Each additional StructureDefinition file builds off of a base
    StructureDefinition and specifies modifications to the base.
    Modifications may include but are not limited to changing cardinality of attributes
    cardinality between referenced Resources, adding new attributes, etc.

2. **Validate the syntax, content, and referential integrity of StructureDefinition**

    The FHIR data model is database/datastore/server agnostic. It is up to the implementer
    to choose the datastore, implement the server, and ensure data going into/coming out
    of the server conforms to the FHIR data model.

    In most cases, the validation to ensure conformance is implemented in the application
    layer of the server and not within the database. To validate a StructureDefinition
    you can use the official FHIR Validator
    http://wiki.hl7.org/index.php?title=Using_the_FHIR_Validator
    or you can choose one of the many FHIR server implementations.

    For this repository we have chosen the latter and will use Firely's
    Vonk FHIR server for validation.


3. **Test Resources against the StructureDefinition**

    This cannot be done with a standalone validation tool and must be done
    on a FHIR server. The only way to accomplish this is to load the
    StructureDefinitions into the chosen FHIR server and try creating
    FHIR Resources to test the StructureDefinitions.

    Again we've chosen Firely's Vonk server to do this. It is a good idea
    to familiarize yourself a little bit with Vonk and how it does validation:

    http://docs.simplifier.net/vonk/features/prevalidation.html

*\*From here on we will refer to StructureDefinition as Profile.*

## Quickstart
This repository essentially contains:
1. Dockerfile and docker-compose files to spin up a local Vonk FHIR server
   and local Mongodb database
2. Python (3.7) based CLI tool that is used to validate
JSON (XML coming soon) based profiles and sample FHIR Resource files.

### Installation
1. Git clone this repository

```bash
git clone git@github.com:kids-first/kf-model-fhir.git
cd kf-model-fhir
```

2. Setup a Python virtual environment

```bash
# Create virtualenv
python3 -m venv venv

# Activate virtualenv
source ./venv/bin/activate
```

3. Install the Python CLI tool

```bash
pip install -e .
```
Test the installation by running the CLI: `fhirmodel -h`. You should see
something that contains:
```
Usage: fhirmodel [OPTIONS] COMMAND [ARGS]...

  A CLI utility for validating FHIR Profiles and Resources
```

4. Install Docker CE: https://docs.docker.com/install/

## Run
1. Spin up FHIR server + Mongodb by running `docker-compose up -d`
2. Add a new profile in `./project/profiles`
3. Validate it by running `fhirmodel validate profile`
4. Add a new example resource to test the profile in `./project/resources`
5. Validate it by running `fhirmodel validate resource`
6. Bring down FHIR server + database by running `docker-compose down`

## Develop
All model files will be stored in the project directory which can be found
at `./project`.

### Note - Simplifier Project
The project directory is called "project" (and not something else like model)
because it represents a Firely Simplifier Project. A Simplifier project
contains profiles, example resources, and later on implementation guides for
a specific version of FHIR. See https://simplifier.net/learn.

Everything in this folder will eventually be synced or published to the corresponding
[KidsFirstSTU3 Simplifier Project](https://simplifier.net/kidsfirststu3) so that stakeholders and collaborators may
view the progress of the model or use it.

More on this later (TODO).


### FHIR Server
Spin up the FHIR server with a Mongodb database: `docker-compose up -d`.
When the service is up you will see a Firely landing page at http://localhost:8080.
You will not need to modify them, but it is useful to know that
FHIR server settings can be found in `./server`. These settings are loaded
when the server starts up.

### Profiles
You can use any tool to develop a profile (Forge, cimpl, etc.), but for example
purposes just create a JSON file in the profile directory called `MyPatient.json`
with the following content:
```json
{
  "resourceType": "StructureDefinition",
  "url": "http://fhirstu3.kids-first.io/fhir/StructureDefinition/PatientProfile",
  "name": "Participant",
  "status": "draft",
  "fhirVersion": "3.0.1",
  "kind": "resource",
  "abstract": false,
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Patient.gender",
        "path": "Patient.gender",
        "min": 1
      },
      {
        "id": "Patient.birthDate",
        "path": "Patient.birthDate",
        "max": "0"
      },
      {
        "id": "Patient.animal",
        "path": "Patient.animal",
        "max": "0"
      }
    ]
  }
}

```
Now validate it by running:
```bash
# Validate all in directory
fhirmodel validate profile

# Or just one file
fhirmodel validate profile --path=./project/profiles/MyPatient.json
```

You should see something like this:
```
2019-07-10 11:22:25,676 - kf_model_fhir.app - INFO - Starting FHIR 3.0.1 profile validation for projects/profiles/MyPatient.json
2019-07-10 11:22:25,927 - kf_model_fhir.app - INFO - Validating FHIR 3.0.1 profile MyPatient.json
2019-07-10 11:22:27,557 - kf_model_fhir.app - INFO - ✅ Validation passed for MyPatient.json
2019-07-10 11:22:27,558 - kf_model_fhir.app - INFO - See validation results in /Users/singhn4/Projects/kids_first/kf-model-fhir/profile_validation_results.json
2019-07-10 11:22:27,558 - kf_model_fhir.cli - INFO - ✅ Profile validation passed!
```

#### * Important - Canonical URLs
The `url` element in a profile is called the canonical URL and used as a
unique identifier for profiles on the server. The server does not check to
see if the URL actually resolves to anything, but it does check to see if
the `url` attribute is present and the value is unique among others loaded
on the server.

### Validation Results
Detailed validation results for both profiles and resources get saved
to JSON files in the current working directory with the following
file naming scheme `[profile | resource]_validation_results.json`

### Log Level
To change the log level go to `kf_model_fhir/config.py` and change it like so:

```python
DEFAULT_LOG_LEVEL = logging.DEBUG
```

### Resources
Create a resource in the resources directory (`./project/resources`)
called `MyPatient.json` with the following content:
```json
{
    "resourceType":"Patient",
    "meta": {
        "profile": "http://fhirstu3.kids-first.io/fhir/StructureDefinition/MyPatient"
    },
    "name": [
        {
            "family":"Flintstones"
        }
    ]
}
```
Now validate it by running:
```bash
# Validate all in directory
fhirmodel validate resource --path=./project/resources
fhirmodel validate resource

# Or just one file
fhirmodel validate resource --path=./project/resources/MyPatient.json
```

You should see that your validation failed for MyPatient.json.
```
2019-07-10 12:29:43,262 - kf_model_fhir.app - INFO - Starting FHIR 3.0.1 resource validation for ./project/resources/MyPatient.json
2019-07-10 12:29:43,263 - kf_model_fhir.app - INFO - Validating FHIR 3.0.1 resource MyPatient.json
2019-07-10 12:29:45,154 - kf_model_fhir.app - INFO - ❌ Validation failed for MyPatient.json
2019-07-10 12:29:45,154 - kf_model_fhir.app - INFO - See validation results in /Users/singhn4/Projects/kids_first/kf-model-fhir/resource_validation_results.json
2019-07-10 12:29:45,154 - kf_model_fhir.cli - ERROR - ❌ Resource validation failed!
```

If you open up `resource_validation_results.json` you'll see this text element:

```"text": "Instance count for 'Patient.gender' is 0, which is not within the specified cardinality of 1..1"
```

in the server's response. This is because we forgot to include a
required attribute, gender.

#### * Important - Reference Profiles
You'll notice that our resource content has a `meta.profile` element. When
you are validating a resource on the FHIR server, you must
specify which profile the resource claims to conform to by providing its
profile's canonical URL in the `meta.profile` element.  

## Publish
TODO:
- Push code to feature branch
- Make pull request, request review
- Merge pull request
- Publish model to Simplifier
- View Simplifier project
