import os
import logging
from collections import defaultdict
from pprint import pformat

import requests
from requests.auth import HTTPBasicAuth

from kf_model_fhir import __fhir_version__ as FHIR_VERSION
from kf_model_fhir.utils import (
    check_service_status,
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


def validate(data_path, resource_type):
    """
    Validate FHIR resources - StructureDefinition(s) (also known as profiles)
    or other Resource(s)

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :param resource_type: must be one of {profile, resource}
    :type resource_type: str
    :returns: a boolean indicating if validation was successful
    """
    # Check service status
    if check_service_status(SERVER_BASE_URL):
        logger.error(f'FHIR validation server {SERVER_BASE_URL} must be '
                     'up in order to continue with validation')
        exit(1)

    data_path = os.path.abspath(os.path.expanduser(data_path))
    logger.info(
        f'Starting FHIR {FHIR_VERSION} {resource_type} validation for '
        f'{data_path}'
    )
    # Gather resource payloads to validate
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

    # Validate
    if resource_type == 'profile':
        # Drop all profiles first
        _delete_all(f'{SERVER_BASE_URL}/{PROFILE_ENDPOINT}',
                    auth=AUTH, params={'url:below': CANONICAL_URL})
        success = _validate(resources, resource_type)
    else:
        success = _validate(resources, resource_type)

    return success


def _read_resource_file(filepath):
    """
    Read XML or JSON FHIR resource file into a dict

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

    Returns whether or all resources passed validation. Write results to
    validation output file.

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
        success, result = _validate_resource(resource_type, resource)

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
    """
    response = requests_retry_session().get(
        endpoint,
        **request_kwargs
    )
    if response.status_code != 200:
        raise Exception(
            f'Failed to delete existing {endpoint}. '
            f'Status code: {response.status_code}, '
            f'Caused by: {response.json()}'
        )

    logger.debug(f'Deleting {response.json()["total"]} {endpoint} ...')
    for entry in response.json().get('entry', []):
        url = f'{endpoint}/{entry["resource"]["id"]}'
        response = requests_retry_session().delete(
            url,
            **request_kwargs
        )
        if response.status_code != 204:
            raise Exception(
                f'Could not delete {url}'
                f'Status code: {response.status_code}, '
                f'Caused by: {response.json()}'
            )
        else:
            logger.debug(f'Deleted {url}')


def _validate_resource(resource_type, resource, auth=AUTH):
    """
    Validate FHIR resource - StructureDefinition or regular resource

    For StructureDefinition create the resource on the server
    For non-StructureDefinition send the resource to the $validate endpoint

    :param resource_type: one of {profile, resource}
    :type resource_type: str
    :returns: tuple containing success boolean and result data. See _post
    """
    if resource_type == 'profile':
        endpoint = f'{SERVER_BASE_URL}/{PROFILE_ENDPOINT}'
    else:
        # TODO
        endpoint = None

    return _post(resource, endpoint)


def _post(payload, endpoint, **request_kwargs):
    """
    POST a FHIR resource to the Vonk server

    :param payload: a dict containing FHIR resource content
    :type payload: dict
    :param endpoint: FHIR endpoint
    :type endpoint: str
    :param request_kwargs: optional request keyword args
    :type request_kwargs: key, value pairs
    :returns: tuple of the form (bool denoting success,
    dict containing success or list of errors)
    """
    request_kwargs['headers'] = {'Content-Type': 'application/json'}
    request_kwargs['json'] = payload
    response = requests_retry_session().post(
        endpoint,
        **request_kwargs
    )
    if response.status_code in {201, 200}:
        output = response.json()
        success = True
        msg = f'POST succeeded: {output["resourceType"]}'
        _id = output.get('id')
        if _id:
            msg += f' id: {output["id"]}'
        logger.debug(msg)
    else:
        output = _errors_from_response(response.json())
        success = False
        logger.debug(
            f'POST failed. Caused by:\n{pformat(output)}'
        )

    return success, output


def _errors_from_response(response_body):
    """
    Comb list of issues in Vonk response and return the ones marked error
    """
    return [issue for issue in response_body['issue']
            if issue['severity'] == 'error']
