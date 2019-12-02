import os
import shutil
import logging
from copy import deepcopy
from random import choice, uniform

from kf_model_fhir.config import (
    SIMPLIFIER_PROJECT_NAME,
    SIMPLIFIER_FHIR_SERVER_URL,
    PROJECT_DIR,
    SERVER_CONFIG
)
from kf_model_fhir.validation import FhirValidator
from kf_model_fhir import loader
from kf_model_fhir.utils import read_json, write_json

logger = logging.getLogger(__name__)


def publish_to_server(resource_dir, resource_type='profile',
                      username=None, password=None,
                      project_name=SIMPLIFIER_PROJECT_NAME,
                      server_name='simplifier',
                      exclude=None):
    """
    Publish resource files in resource_dir to Simplifier.net project

    Profiles are published by running validation since validation creates
    profiles on the server

    :param resource_dir: directory containing FHIR resource files
    :type resource_dir: str
    :param resource_type: directory containing FHIR resource files
    :type resource_type: str
    :param username: Simplifier account username
    :type username: str
    :param password: Simplifier account password
    :type password: str
    :param project_name: Simplifier project_name
    :type project_name: str

    :returns: a boolean indicating if publish was successful
    """
    server_cfg = SERVER_CONFIG.get(server_name)
    base_url = server_cfg.get('base_url')

    if server_name == 'simplifier':
        project_name = ''.join(project_name.split(' '))
        base_url = f'{SIMPLIFIER_FHIR_SERVER_URL}/{project_name}'

    logger.info(
        f'Begin publishing {resource_type} in {resource_dir} '
        f'to Simplifier project {base_url}'
    )

    success = True
    fhir_validator = FhirValidator(
        server_cfg=server_cfg,
        username=username,
        password=password
    )
    client = fhir_validator.client

    # Publish profiles to fhir server
    if resource_type == 'profile':
        return fhir_validator.validate(
            'profile', resource_dir, exclude=exclude
        )

    # Publish resources to fhir server
    else:
        # Delete all existing resources
        order = [
            'ResearchStudy', 'Patient', 'ResearchSubject',
            'Specimen', 'Observation', 'Condition'
        ]
        resources = loader.load_resources(resource_dir)
        ordered = {
            rt: [r for r in resources if r['resource_type'] == rt]
            for rt in order
        }

        for rt in reversed(list(ordered.keys())):
            resources = ordered[rt]
            for rd in resources:
                rd['endpoint'] = (
                    f"{base_url}/{rd['resource_type']}/{rd['content']['id']}"
                )
                success_delete, _ = client.send_request(
                    'delete', rd['endpoint']
                )
                if not success_delete:
                    logger.warning(
                        f'⚠️ Failed to delete resource at {rd["endpoint"]}'
                    )
                success = success_delete & success

        for resources in ordered.values():
            success_create_all, _ = client.post_or_put_all(resources,
                                                           method='put')
            success = success_create_all & success

    return success


def generate(resource_dir, patients=10):
    """
    Temporary
    """
    specimens_per_pt = 2
    conditions_per_pt = 1
    observation_per_bs = 1

    template_dir = os.path.join(PROJECT_DIR, 'template')
    templates = {
        fn.split('.')[0].lower(): read_json(os.path.join(template_dir, fn))
        for fn in os.listdir(template_dir)
    }

    # Clear out resources
    resource_dir = os.path.abspath(os.path.expanduser(resource_dir))
    if os.path.isdir(resource_dir):
        shutil.rmtree(resource_dir)
    os.makedirs(resource_dir)

    studies = []
    for s in range(2):
        study = create_study(templates, s)
        studies.append(study)
        fp = os.path.join(resource_dir, f'ResearchStudy-{study["id"]}.json')
        write_json(study, fp)
        logger.info(f'Created research study {study["id"]}')

    # Make resources
    for i in range(patients):
        # Patient
        patient = create_patient(templates, i)
        fp = os.path.join(resource_dir, f'Patient-{patient["id"]}.json')
        write_json(patient, fp)
        logger.info(f'Created patient {patient["id"]}')

        # ResearchSubject
        if i % 2:
            study_id = studies[0]['id']
        else:
            study_id = studies[1]['id']
        subject = create_research_subj(templates, i, patient["id"], study_id)
        fp = os.path.join(
            resource_dir, f'ResearchSubject-{subject["id"]}.json'
        )
        write_json(subject, fp)
        logger.info(f'Created research subject {subject["id"]}')

        # Specimens for patient
        for j in range(specimens_per_pt):
            specimen = create_specimen(templates, f'{i}-{j}', patient["id"])
            fp = os.path.join(resource_dir, f'Specimen-{specimen["id"]}.json')
            write_json(specimen, fp)
            logger.info(f'Created specimen {specimen["id"]}')

            # Observation for specimen
            for o in range(observation_per_bs):
                obs = create_observation(templates, f'{i}-{o}', specimen["id"])
                fp = os.path.join(
                    resource_dir, f'Observation-{obs["id"]}.json'
                )
                write_json(obs, fp)
                logger.info(f'Created observation {obs["id"]}')

        # Condition for patient
        for k in range(conditions_per_pt):
            condition = create_condition(templates, f'{i}-{k}', patient["id"])
            fp = os.path.join(
                resource_dir, f'Condition-{condition["id"]}.json'
            )
            write_json(condition, fp)
            logger.info(f'Created condition {condition["id"]}')


def create_study(templates, i):
    """
    Create a research study
    """
    study = deepcopy(templates['researchstudy'])
    _id = f'SD-0000{i}'
    study['id'] = _id
    study['identifier'] = [{'value': _id}]
    study['title'] = f'Research Study {_id}'
    return study


def create_patient(templates, i):
    """
    Create a patient
    """
    patient = deepcopy(templates['patient'])
    race = deepcopy(choice(templates['race']))
    ethnicity = deepcopy(choice(templates['ethnicity']))

    pid = f'PT-0000{i}'
    patient['id'] = pid
    patient['identifier'] = [{'value': pid}]
    patient['gender'] = choice(['male', 'female'])
    patient['name'] = [{
        "family": choice(['Foofoo', 'Holmes', 'Barbaz']),
        "given": [choice(['Natasha', 'Ninoshka', 'Allison',
                          'Dan', 'Alex', 'Avi', 'Meen', 'Ben'])]
    }]
    patient['extension'].extend(
        [
            {
                "url": "http://fhirr4.kids-first.io/fhir/StructureDefinition/us-core-race",
                "extension": [
                    {
                        'valueString': race['valueCoding']['display'],
                        'url': 'text'
                    },
                    race
                ]
            },
            {
                "url": "http://fhirr4.kids-first.io/fhir/StructureDefinition/us-core-ethnicity",
                "extension": [
                    {
                        'valueString': ethnicity['valueCoding']['display'],
                        'url': 'text'
                    },
                    ethnicity
                ]
            }
        ]
    )
    return patient


def create_research_subj(templates, i,  patient_id, study_id):
    """
    Create a research subject
    """
    subject = deepcopy(templates['researchsubject'])
    _id = f'RS-0000{i}'
    subject['id'] = _id
    subject['identifier'] = [{'value': _id}]
    subject['individual'] = {'reference': f'Patient/{patient_id}'}
    subject['study'] = {'reference': f'ResearchStudy/{study_id}'}
    return subject


def create_specimen(templates, i, patient_id):
    """
    Create a specimen for a patient
    """
    template = templates['specimen']
    specimen = deepcopy(template['Specimen'])
    _id = f'BS-0000{i}'
    specimen['id'] = _id
    specimen['identifier'] = [{'value': _id}]
    specimen['subject'] = {
        'reference': f'Patient/{patient_id}'
    }
    specimen['extension'].append(
        {
            "url": "http://fhirr4.kids-first.io/fhir/StructureDefinition/specimen-analyte-type",
            "valueString": choice(['DNA', 'RNA'])
        }
    )
    specimen['collection']['bodySite'] = deepcopy(choice(template['bodySite']))
    return specimen


def create_condition(templates, i, patient_id):
    """
    Create a condition for a patient
    """
    template = templates['condition']
    condition = deepcopy(template['Condition'])
    _id = f'CD-0000{i}'
    condition['id'] = _id
    condition['identifier'] = [{'value': _id}]
    condition['subject'] = {
        'reference': f'Patient/{patient_id}'
    }
    condition['code'] = deepcopy(choice(template['codes']))
    # Update date
    # TODO

    return condition


def create_observation(templates, i, specimen_id):
    """
    Create a observation about a specimen
    """
    observation = deepcopy(templates['observation'])
    _id = f'OB-0000{i}'
    observation['id'] = _id
    observation['identifier'] = [{'value': _id}]
    observation['specimen'] = {
        'reference': f'Specimen/{specimen_id}'
    }
    observation.pop('subject', None)
    observation['valueQuantity']['value'] = round(uniform(3, 6), 2)

    # Update date
    # TODO

    return observation
