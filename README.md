# 🔥 Kids First FHIR Data Model

This is an experimental repository for developing the Kids First
FHIR data model for FHIR version STU3. The model consists of:

- FHIR [conformance resources](http://hl7.org/fhir/STU3/conformance-module.html) - which we call "profiles"
- Non-conformance FHIR resources - which we call "resources"

Kids First will use the Firely technology stack: https://simplifier.net/downloads
to implement and validate the model.

## Quickstart
This repository primarily contains:
1. The profile and resource files that make up the Kids First FHIR data model
2. Python (3.7) based CLI tool that is used to validate profile and resource
files (can be JSON or XML).
3. Server settings and docker-compose files to spin up a local Vonk FHIR server
 and a local Mongodb database which are used for validation

### Installation
1. Git clone this repository

```bash
$ git clone git@github.com:kids-first/kf-model-fhir.git
$ cd kf-model-fhir
```

2. Setup a Python virtual environment

```bash
# Create virtualenv
$ python3 -m venv venv

# Activate virtualenv
$ source ./venv/bin/activate
```

3. Install the Python CLI tool

```bash
$ pip install -e .
```
Test the installation by running the CLI: `fhirmodel -h`. You should see
something that contains:
```
Usage: fhirmodel [OPTIONS] COMMAND [ARGS]...

  A CLI utility for validating FHIR Profiles and Resources
```

4. Install Docker CE: https://docs.docker.com/install/

### Create a Simplifier Account + Project
Each developer will need their own evaluation license file to run the
Vonk server for local development:

1. Go to `http://www.simplifier.net` and create an account
2. Login to your account and create a Simplifer project
    - You must use FHIR version: STU3
3. Download the server license for your project
    - Go to `http://www.simplifier.net/<your-project-name>`
    - Click the Download button on the right, and then click
    `<your-project-name> FHIR server` menu item in the download menu
    - Click the orange Download button to download the server zip
4. Copy the license file to your local repo
    - Unzip the archive and copy the license folder to ./server
    - You should have `./server/license/vonk-trial-license.json`

### Run Validation
1. Spin up FHIR server + db by running `docker-compose up -d`
2. Add a new profile in `./project/profiles`
3. Validate it by running `fhirmodel validate profile`
4. Add a new example resource to test the profile in `./project/resources`
5. Validate it by running `fhirmodel validate resource`
6. Bring down FHIR server + database by running `docker-compose down`


## About FHIR
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


## Develop

### Version Control
Similar to other Kids First code repository, this repository will use Git flow
for collaborative code development and version control.  Please review
the [Kids First Developer Handbook](https://kids-first.github.io/kf-developer-handbook/development/feature_lifecycle.html) if you are not familiar with this.

### Project Directory
All model files will be stored in the project directory, `./project`    

The project directory is called "project" (and not something else like model)
because it represents a Firely Simplifier Project. A Simplifier project
contains FHIR profiles, example resources, and implementation guides for
a specific version of FHIR. See https://simplifier.net/learn.

Everything we put in this folder will eventually be published to the corresponding
[KidsFirstSTU3 Simplifier Project](https://simplifier.net/kidsfirststu3) so that
stakeholders and collaborators may view the progress of the model or use it.

### FHIR Server

#### Server settings
Server settings can be controlled by modifying `server/appsettings.json`
and `server/logsettings.json`. You will likely never need to change these settings

#### Spin up the server
Spin up the FHIR server with a Mongodb database by running:

```bash
$ docker-compose up -d
```
When the service is up you will see a Firely landing page at http://localhost:8080.

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
Now validate it by running one of the following:
```bash
# Validate a single profile file
$ fhirmodel validate profile --path=./project/profiles/MyPatient.json

# OR validate all profiles in a specific directory
$ fhirmodel validate profile --path=./project/profiles

# OR validate all profiles in the default profile directory
$ fhirmodel validate profile
```

You should see something like this:
```
2019-07-12 19:53:31,751 - kf_model_fhir.app - INFO - Starting FHIR 3.0.1 profile validation for /Users/singhn4/Projects/kids_first/kf-model-fhir/project/profiles
2019-07-12 19:53:31,890 - kf_model_fhir.app - INFO - Validating FHIR 3.0.1 StructureDefinition from Participant.json
2019-07-12 19:53:33,374 - kf_model_fhir.app - INFO - ✅ POST Participant.json to http://localhost:8080/administration/StructureDefinition succeeded
2019-07-12 19:53:33,375 - kf_model_fhir.app - INFO - See validation results in /Users/singhn4/Projects/kids_first/kf-model-fhir/profile_validation_results.json
2019-07-12 19:53:33,375 - kf_model_fhir.cli - INFO - ✅ Profile validation passed!
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
Read more about [Python logging levels here.](https://docs.python.org/3.7/library/logging.html#logging-levels)

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
Now validate it by running one of the following:
```bash
# Validate a single resource file
$ fhirmodel validate resource --path=./project/resources/MyPatient.json

# OR validate all resources in a specific directory
$ fhirmodel validate resource --path=./project/resources

# OR validate all resources in the default resource directory
$ fhirmodel validate resource
```

You should see that your validation failed for MyPatient.json.
```
2019-07-12 19:57:49,020 - kf_model_fhir.app - INFO - Starting FHIR 3.0.1 resource validation for ./project/resources/MyPatient.json
2019-07-12 19:57:49,021 - kf_model_fhir.app - INFO - Validating FHIR 3.0.1 Patient from MyPatient.json
2019-07-12 19:57:49,833 - kf_model_fhir.app - INFO - ❌ POST MyPatient.json to http://localhost:8080/Patient/$validate failed
2019-07-12 19:57:49,835 - kf_model_fhir.app - INFO - See validation results in /Users/singhn4/Projects/kids_first/kf-model-fhir/resource_validation_results.json
2019-07-12 19:57:49,835 - kf_model_fhir.cli - ERROR - ❌ Resource validation failed!
```

If you open up `resource_validation_results.json` you'll see this:

```
"text": "Instance count for 'Patient.gender' is 0, which is not within the specified cardinality of 1..1"
```

in the server's response. This is because we forgot to include a
required attribute, gender. Try adding `"gender": "female"` to the resource
and re-running validation. It should pass.

#### * Important - Reference Profiles
You'll notice that our resource content has a `meta.profile` element. When
you are validating a resource on the FHIR server, you must
specify which profile the resource claims to conform to by providing its
profile's canonical URL in the `meta.profile` element.  


## Publish

### Push to Your Simplifier Project
Simplifier provides some very useful graphical views of your profiles that
help you see the differences between your profile and the base profile that your
profile extends. While you're developing your profiles you may want to push
them to your Simplifier project so you can make use of these views:

```
fhirmodel publish ./project/profiles --username=$SIMPLIFIER_USER --password=$SIMPLIFIER_PW --project=<Simplifier Project Name>
```

### Pull Requests
You should already have a local git branch (e.g. add-biospecimen-profiles-resources)
that you've been periodically committing to and pushing up to Github. At this point
you're ready to get your code merged into the master branch of the git repository.  

Go ahead and make a Pull Request on Github to merge your feature branch into
the master branch. If you're not quite ready for it to be reviewed, you can
make it a [Draft Pull Request](https://help.github.com/en/articles/about-pull-requests#draft-pull-requests).

Once all status checks have passed, request review(s) from other
model developers. You need at least 1 approving review to merge your PR.

### Continuous Integration
Notice the status checks section of the Pull Request:
<p align="center">
  <img src="docs/images/status-check.png" alt="GitHub Pull Request Status Check" width="90%">
</p>

Every pull request must pass all of the status checks before it is eligible for
merging. For this repository there is only one status check: every time you
push a commit, the continuous integration that has been setup runs profile and
resource validation on the `./projects` directory
using the same Python CLI tool you've been using.

We use CircleCI for our CI solution.
If you click on the "Details" link next to `ci/circleci: build` text, you can
see a more detailed view of the CI output on CircleCI.

### Publish to the Kids First Simplifier Project
Once you have an approving review and all status checks have passed you may
merge your Pull Request. Once again, CI will run but this time on the master
branch (since its been updated with your code).

Any time CI runs on the master branch it will do one additional step. If
validation passes, it will publish all of the profile and resource files
in the `./project` directory to the
[Kids First STU3 Simplifier Project](https://simplifier.net/kidsfirststu3).
