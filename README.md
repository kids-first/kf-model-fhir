<p align="center">
  <img src="docs/images/logo.svg" alt="Kids First FHIR Data Model" width="660px">
</p>
<p align="center">
  <a href="https://github.com/kids-first/kf-model-fhir/blob/master/LICENSE"><img src="https://img.shields.io/github/license/kids-first/kf-model-fhir.svg?style=for-the-badge"></a>
  <a href="https://circleci.com/gh/kids-first/kf-model-fhir"><img src="https://img.shields.io/circleci/project/github/kids-first/kf-model-fhir.svg?style=for-the-badge"></a>
</p>

# Kids First FHIR Data Model

This is an experimental repository for developing the Kids First
FHIR data model for FHIR version R4. The model consists of:

- FHIR [conformance resources](http://hl7.org/fhir/R4/conformance-module.html) -
  which we call "profiles"
- Non-conformance FHIR resources - which we call "example resources"

## FHIR 101 - Practical Guide

If you have never heard of FHIR or are unfamiliar with how to implement FHIR, checkout the [FHIR 101 Jupyter Notebook](https://github.com/kids-first/kf-model-fhir/tree/master/docs/fhir-guide).

## Quickstart
This repository contains:
1. Kids First FHIR Data Model - the profile and example resource files
2. Kids First Data Model Docs Site - The HTML/CSS/JavaScript files needed to
   generate a Jekyll documentation site for the model. This is also known as
   a `FHIR Implementation Guide` (IG).
3. Python (3.7) based CLI tool that has commands to make it easier to validate
   the FHIR data model, add resources to the docs site, convert between json/xml,
   and publish resources to a FHIR server.

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

### Run Validations
The files that make up the FHIR data model are enclosed inside the default root
directory for the IG: `./site_root`

1. Add a new profile

    `./site_root/source/resources/<resource file>`

2. Add the necessary configuration to the IG for the resource

   `fhirmodel add ./site_root/source/resources/<resource file>`

3. Add a new example resource to test the profile

    `./site_root/source/examples`

4. Add the necessary configuration to the IG for the resource

   `fhirmodel add --is_example ./site_root/source/examples/<resource file>`

5. Validate the models

   `fhirmodel validate ./site_root/ig.json --publisher_opts='-tx n/a'`

## About FHIR
FHIR is an HL7 data interoperability specification which includes a definition of
a base data model and a standard for a RESTful API to
interact with FHIR data that conforms to the model. See https://www.hl7.org/fhir/.


### Data Model
The base FHIR data model consists of a set of XML/JSON files that specify
FHIR entity (called a Resource) definitions, referential constraints between
Resources, and constraints on Resource attributes.

See https://www.hl7.org/fhir/resourcelist.html.

Conformance resources such as `StructureDefinition`, `SearchParameter`, etc
are very often called **"Profiles"** colloquially. The term **"Resource"**
often refers to non-conformance FHIR resources such as `Patient`, `Specimen`, etc.

The FHIR data model is database/datastore/server agnostic. It is up to the implementer
to choose the datastore, implement the server, and ensure data going into/coming out
of the server conforms to the FHIR data model.

### RESTful Server
The FHIR specification describes a RESTful interface for performing basic
transactions on the data like: create, read, update, delete. The specification
also describes a RESTful interface for performing detailed search operations
on the data.

Again, FHIR is technology agnostic and has no opinions on how this should be
implemented.

Additionally, in most cases all validation to ensure conformance is implemented in the
application layer of the server and not within the database.


### Model Development
To "develop" a FHIR data model means to:

1. **Create additional conformance resource file(s)**

    If you look at the base model, you'll notice that the constraints are very
    loose (almost nothing is required). This might not be ideal for real world
    use cases.

    Each additional `StructureDefinition` file builds off of a base
    `StructureDefinition` and specifies modifications to the base.

    Modifications may include but are not limited to changing cardinality of attributes
    cardinality between referenced Resources, adding new attributes, etc.

2. **Validate the syntax, content, and referential integrity of conformance resources**

    After conformance resources are authored, it is important to validate them
    to 1) ensure they are FHIR compliant and 2) that they do what we expect.

    To do 1 above, we simply submit the resource to a FHIR validation tool.   

    This repository uses the official [HL7 FHIR IG Publisher](https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation) for validation.

3. **Test resources against the conformance resources**

    To ensure the conformance resources do what we expect, we need to test them
    against example resources. For example if we have a StructureDefinition for
    the Patient resource which requires a value for gender and race attributes,
    then we will test an invalid example Patient resource
    (bound to the Patient StructureDefinition) which is missing these values
    and a valid Patient resource which has both these values. The first test
    should fail while the second should pass.

### Model Documentation
The FHIR spec includes standards for how a FHIR data model should be documented.
FHIR data models are documented via an **Implementation Guide** which is essentially
a FHIR compliant static website. FHIR also has a conformance resource called `ImplementationGuide`
which contains configuration information for this docs site.

Implementation Guides may be generated using the [HL7 FHIR IG Publisher](https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation). The current HL7 IG Publisher uses [Jekyll](https://jekyllrb.com/docs/)
to generate the docs site.

## Develop
This repository provides a Python based CLI and process for accomplishing the above
model development and documentation process.

### Version Control
Similar to other Kids First code repository, this repository will use Git flow
for collaborative code development and version control.  Please review
the [Kids First Developer Handbook](https://kids-first.github.io/kf-developer-handbook/development/feature_lifecycle.html) if you are not familiar with this.

### Repository Layout

- Source code for CLI: `kf_model_fhir`
- Source files for IG: `site_root`
- Implementation Guide control file: `./site_root/ig.json`
- Implementation Guide resource: `./site_root/source/resource/implementationguide/kidsfirst.json`
- Profiles: `./site_root/source/resource`
- Example resources: `./site_root/source/examples`

### IG Control and Resource Files
These two files contain configuration information for the IG and affect which
resources are validated and included in the generated site.
Read more about them [here](https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation#IGPublisherDocumentation-Controlfile) and [here](http://www.hl7.org/fhir/implementationguide.html)

### Profiles
You can use any tool to develop a profile (Forge, cimpl, etc.), but for example
purposes just create a JSON file in the profile directory:

 `./site_root/source/resources/StructureDefinition-ResearchStudy.json`

with the following content:
```json
{
    "resourceType": "StructureDefinition",
    "url": "http://fhir.kids-first.io/StructureDefinition/ResearchStudy",
    "version": "0.1.0",
    "name": "ResearchStudy",
    "title": "Research Study",
    "status": "draft",
    "publisher": "Kids First",
    "description": "A research study within the Kids First ecosystem",
    "fhirVersion": "4.0.0",
    "kind": "resource",
    "abstract": false,
    "type": "ResearchStudy",
    "baseDefinition": "http://hl7.org/fhir/StructureDefinition/ResearchStudy",
    "derivation": "constraint",
    "differential": {
        "element": [
            {
                "id": "ResearchStudy",
                "path": "ResearchStudy"
            },
            {
                "id": "ResearchStudy.arm",
                "path": "ResearchStudy.arm",
                "max": "0"
            },
            {
                "id": "ResearchStudy.phase",
                "path": "ResearchStudy.phase",
                "max": "0"
            }
        ]
    }
}
```

#### * Important - Canonical URLs
The `url` element in a profile is called the canonical URL and used as a
unique identifier for profiles on the server. The server does not check to
see if the URL actually resolves to anything, but it does check to see if
the `url` attribute is present and the value is unique among others loaded
on the server.

### Resources
Next create a resource in the example resources directory

`./site_root/source/examples/research-study-example.json`

with the following content:

```json
{
    "resourceType":"ResearchStudy",
    "id": "research-study-example",
    "meta": {
        "profile": ["http://fhir.kids-first.io/StructureDefinition/ResearchStudy"]
    },
    "status": "completed",
    "title": "Study of Ewing's Sarcoma"
}

```
### Validate

To validate the conformance resource along with the example resource you just
created, run the following:

```
# Add resource configuration to IG
fhirmodel add ./site_root/source/resources/StructureDefinition-ResearchStudy.json
fhirmodel add ./site_root/source/examples/research-study-example.json

# Run publisher to validate
fhirmodel validate ./site_root/ig.json --publisher_opts='-tx n/a'
```
The `add` command adds boilerplate configuration for the resources to the IG
control file, IG resource file, and creates the expected markdown files. This
is necessary for the resource to be included in validation and in the the
generated IG site

### Validation Results
The CLI will log output to the screen and tell you whether validation succeeded or failed.
You can view detailed validation results at `./site_root/output/qa.html`

### Log Level
To change the log level go to `kf_model_fhir/config.py` and change it like so:

```python
DEFAULT_LOG_LEVEL = logging.DEBUG
```
Read more about [Python logging levels here.](https://docs.python.org/3.7/library/logging.html#logging-levels)

## Publish

Many FHIR data models in the FHIR ecosystem use [Simplifier](https://simplifier.net/)
as a platform for publishing and distributing their data model. Simplifier
also provides some nice views of the conformance resources which show
how they differ from the base resource they are extending. This can be
very useful for debugging.

### Create a Simplifier Account + Project
Each developer will need their own Simplifier account and project if they want
to publish their data model files for debugging/viewing:

1. Go to `http://www.simplifier.net` and create an account
2. Login to your account and create a Simplifier project
    - You must use FHIR version: R4

### Push to Your Simplifier Project
Publish both the conformance resources and example resources to Simplifier
```
fhirmodel publish ./site_root/source/resources --username=$SIMPLIFIER_USER --password=$SIMPLIFIER_PW --base_url=<your server>
fhirmodel publish ./site_root/source/examples --username=$SIMPLIFIER_USER --password=$SIMPLIFIER_PW --base_url=<your server>s
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
resource validation for the model using the same Python CLI tool you've been using.

We use CircleCI for our CI solution.
If you click on the "Details" link next to `ci/circleci: build` text, you can
see a more detailed view of the CI output on CircleCI.

### Publish to the Kids First Simplifier Project
Once you have an approving review and all status checks have passed you may
merge your Pull Request. Once again, CI will run but this time on the master
branch (since its been updated with your code).

Any time CI runs on the master branch it will do one additional step. If
validation passes, it will publish all of the profile and resource files
in the `./site_root/source` directory to the
[Kids First R4 Simplifier Project](https://simplifier.net/kidsfirstr4).
