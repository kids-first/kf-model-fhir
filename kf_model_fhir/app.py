import os
import logging
from collections import defaultdict
from pprint import pformat

import requests
from requests.auth import HTTPBasicAuth

from kf_model_fhir import __fhir_version__ as FHIR_VERSION
from kf_model_fhir.utils import (
    requests_retry_session,
    read_json,
    write_json
)
from kf_model_fhir.config import (
    SIMPLIFIER_USER,
    SIMPLIFIER_PW,
    CANONICAL_URL,
    SERVER_BASE_URL,
    PROFILE_ENDPOINT,
    VALIDATION_RESULTS_FILES
)

AUTH = HTTPBasicAuth(SIMPLIFIER_USER, SIMPLIFIER_PW)
logging.getLogger(
    requests.packages.urllib3.__package__).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def validate_profiles(data_path):
    """
    Validate FHIR StructureDefinition(s) - also called profiles

    Load StructureDefinition files into tuples (filename, dict)
    Delete existing profiles on validation FHIR server
    Validate by POSTing new profiles on FHIR server

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :returns: a boolean indicating if validation was successful
    """
    logger.info(
        f'Starting FHIR {FHIR_VERSION} profile validation for '
        f'{data_path}'
    )
    # Gather profile payloads to validate
    resources = load_resources(data_path)

    # Drop all profiles first
    success = _delete_all(f'{SERVER_BASE_URL}/{PROFILE_ENDPOINT}',
                          auth=AUTH, params={'url:below': CANONICAL_URL})
    if not success:
        logger.error('Failed to delete existing profiles. Exiting')
        exit(1)

    # Validate profiles
    return _validate(resources, 'profile')


def validate_resources(data_path):
    """
    Validate FHIR Resources against profiles

    Load FHIR resource files into tuples (filename, dict)
    Check each resource has a referenced profile in its meta.profile element
    Validate by POSTing to /<resource name>/$validate

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :returns: a boolean indicating if validation was successful
    """
    logger.info(
        f'Starting FHIR {FHIR_VERSION} resource validation for '
        f'{data_path}'
    )

    # Gather resource payloads to validate
    resources = load_resources(data_path)

    # Check that each resource has a referenced profile
    for file_name, resource in resources:
        rt = resource.get("resourceType")
        metadata = resource.get('meta', {})
        if 'profile' not in metadata:
            profile_uri = f'{CANONICAL_URL}/StructureDefinition/{rt}'
            display = {'meta': {'profile': profile_uri}}
            raise Exception(
                f"Profile canonical url not found in {file_name}. "
                "When validating a resource, you must specify which profile "
                f"to use via its canonical URL. You can do this by adding the "
                f"'meta' object to your resource payload. "
                f"An example looks like: {pformat(display)} "
            )

    return _validate(resources, 'resource')


def load_resources(data_path):
    """
    Read resource files from disk and create list of tuples
    (resource filename, resource dict)

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :returns: a boolean indicating if validation was successful
    """
    data_path = os.path.abspath(os.path.expanduser(data_path))
    resources = []
    if not os.path.isdir(data_path):
        file_dir, file_name = os.path.split(data_path)
        file_names = [file_name]
    else:
        file_dir = data_path
        file_names = os.listdir(data_path)
    for f in file_names:
        if f in {'package.json', 'fhirpkg.lock.json'}:
            continue
        resource = _read_resource_file(os.path.join(file_dir, f))
        if resource:
            resources.append((f, resource))
    return resources


def _read_resource_file(filepath):
    """
    Read XML or JSON FHIR resource file into a dict.

    :param filepath: path to the resource file
    :type filepath: str
    :returns: dict with resource content
    """
    _, filename = os.path.split(filepath)
    file_ext = os.path.splitext(filename)[-1]
    resource = None

    if file_ext == '.json':
        resource = read_json(filepath)
    elif file_ext == '.xml':
        logger.warning(
            f'Skipping {filename}, {file_ext} files not yet supported'
        )
    else:
        logger.warning(
            f'Skipping {filename}, {file_ext} is an invalid file type'
        )

    return resource


def _validate(resources, resource_type, auth=AUTH):
    """
    Validate FHIR resources

    Returns whether all resources passed validation. Write results to
    validation output file located in current working directory and named:
    <resource_type>_validation_results.json

    :param resources: list of resource dicts
    :type resources: list
    :param resource_type: one of {profile, resource}
    :type resource_type: str
    :param auth: basic auth parameters
    :type auth: requests.auth.HTTPBasicAuth object
    :returns: a boolean denoting whether the validation succeeded
    """
    # Validate
    results = defaultdict(dict)
    for filename, resource in resources:
        logger.info(
            f'Validating FHIR {FHIR_VERSION} {resource_type} {filename}'
        )

        if resource_type == 'profile':
            endpoint = f'{SERVER_BASE_URL}/{PROFILE_ENDPOINT}'
        else:
            rt = resource.get("resourceType")
            endpoint = f'{SERVER_BASE_URL}/{rt}/$validate'

        success, result = _post(resource, endpoint)

        if success:
            logger.info(f'✅ Validation passed for {filename}')
            results['success'][filename] = result
        else:
            logger.info(f'❌ Validation failed for {filename}')
            results['errors'][filename] = result

    # Write results
    if results:
        results_filepath = os.path.join(
            os.getcwd(), VALIDATION_RESULTS_FILES.get(resource_type)
        )
        write_json(results, results_filepath)
        logger.info(f'See validation results in {results_filepath}')

    success = 'errors' not in results
    return success


def _delete_all(endpoint, **request_kwargs):
    """
    Delete FHIR resources at endpoint on Vonk server

    :param endpoint: FHIR endpoint
    :type endpoint: str
    :param request_kwargs: optional request keyword args
    :type request_kwargs: key, value pairs
    :returns: a boolean denoting whether the validation succeeded
    """
    success = True
    response = requests_retry_session().get(
        endpoint,
        **request_kwargs
    )
    if response.status_code != 200:
        logger.warning(
            f'Failed to fetch existing {endpoint}. '
            f'Status code: {response.status_code}, '
            f'Caused by: {response.text}'
        )
        success = False

    logger.debug(f'Deleting {response.json()["total"]} {endpoint} ...')
    for entry in response.json().get('entry', []):
        url = f'{endpoint}/{entry["resource"]["id"]}'
        response = requests_retry_session().delete(
            url,
            **request_kwargs
        )
        if response.status_code != 204:
            logger.warning(
                f'Could not delete {url}'
                f'Status code: {response.status_code}, '
                f'Caused by: {response.text}'
            )
            success = False
        else:
            logger.debug(f'Deleted {url}')

    return success


def _post(payload, endpoint, **request_kwargs):
    """
    POST a FHIR resource to the Vonk server

    :param payload: a dict containing FHIR resource content
    :type payload: dict
    :param endpoint: FHIR endpoint
    :type endpoint: str
    :param request_kwargs: optional request keyword args
    :type request_kwargs: key, value pairs
    :returns: tuple of the form (bool denoting success, response content dict)
    """
    request_kwargs['headers'] = {'Content-Type': 'application/json'}
    request_kwargs['json'] = payload
    response = requests_retry_session().post(
        endpoint,
        **request_kwargs
    )
    success = False
    output = response.json()
    if response.status_code in {201, 200}:
        errors = _errors_from_response(output)
        if not errors:
            success = True
            logger.debug(
                f'POST {endpoint} succeeded. Response:\n{pformat(output)}'
            )
        else:
            logger.debug(
                f'POST {endpoint} failed. Caused by:\n{pformat(output)}'
            )
    else:
        logger.debug(
            f'POST {endpoint} failed, status {response.status_code}. '
            f'Caused by:\n{pformat(response.text)}'
        )

    return success, output


def _errors_from_response(response_body):
    """
    Comb list of issues in Vonk response and return the ones marked error
    """
    return [issue for issue in response_body.get('issue', [])
            if issue['severity'] == 'error']
