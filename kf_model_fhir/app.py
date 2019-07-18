import os
import json
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
    SIMPLIFIER_PROJECT_NAME,
    SIMPLIFIER_FHIR_SERVER_URL,
    CANONICAL_URL,
    SERVER_BASE_URL,
    PROFILE_ENDPOINT,
    VALIDATION_RESULTS_FILES
)

logging.getLogger(
    requests.packages.urllib3.__package__).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def publish_to_simplifier(resource_dir, resource_type='profile',
                          username=None, password=None,
                          project_name=None):
    """
    Publish resource files in resource_dir to Simplifier.net project

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
    project_name = project_name or SIMPLIFIER_PROJECT_NAME
    project_name = ''.join(project_name.split(' '))
    base_url = f'{SIMPLIFIER_FHIR_SERVER_URL}/{project_name}'

    if username and password:
        auth = HTTPBasicAuth(username, password)

    logger.info(
        f'Begin publishing {resource_type} in {resource_dir} '
        f'to Simplifier project {base_url}'
    )

    # Load resources
    resource_dicts = load_resources(resource_dir)

    if len(resource_dicts) == 0:
        logger.info('0 resources loaded. Nothing to publish')
        return True

    success = True
    # Publish profiles to simplifier
    if resource_type == 'profile':

        for rd in resource_dicts:
            rd['endpoint'] = f'{base_url}/StructureDefinition'
        success = validate_profiles(resource_dicts,
                                    base_url,
                                    auth=auth) and success
    # Publish resources to simplifier
    else:
        for rd in resource_dicts:
            rd['endpoint'] = f'{base_url}/{rd["resource_type"]}'
            # Delete all resources
            success = _delete_all(rd['endpoint'], auth=auth)
            if not success:
                logger.error('Failed to delete existing resources. Exiting')
                exit(1)
            # Validate and POST new resources
            success = validate_resources(resource_dicts,
                                         base_url,
                                         auth=auth) and success
    return success


def validate(data_path, resource_type, base_url=SERVER_BASE_URL, auth=None):
    """
    Validate FHIR profiles (StructureDefinitions) or regular FHIR resources

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :param resource_type: Type of data, one of {profile, resource}
    :type resource_type: str
    :param base_url: FHIR server base URL
    :type base_url: str
    :param auth: basic auth parameters obj
    :type auth: requests.auth.HTTPBasicAuth

    :returns: a boolean indicating if validation was successful
    """
    logger.info(
        f'Starting FHIR {FHIR_VERSION} {resource_type} validation for '
        f'{data_path}'
    )

    # Gather resource payloads to validate
    resource_dicts = load_resources(data_path)

    if len(resource_dicts) == 0:
        logger.info('0 resources loaded. Nothing to validate')
        return True

    if resource_type == 'profile':
        success = validate_profiles(resource_dicts, base_url, auth=auth)
    else:
        success = validate_resources(resource_dicts, base_url, auth=auth)

    return success


def validate_profiles(resource_dicts, base_url, auth=None):
    """
    Validate FHIR StructureDefinition(s) - also called profiles

    Delete existing profiles on validation FHIR server
    Validate by POSTing new profiles on FHIR server

    :param resource_dicts: list of dicts containing resources loaded from
    files
    :type resource_dicts: list of dicts
    :param base_url: FHIR server base URL
    :type base_url: str
    :param auth: basic auth parameters obj
    :type auth: requests.auth.HTTPBasicAuth

    :returns: a boolean indicating if validation was successful
    """
    endpoint = resource_dicts[0].get('endpoint')
    if not endpoint:
        for rd in resource_dicts:
            rd['endpoint'] = f'{base_url}/{PROFILE_ENDPOINT}'
        endpoint = rd['endpoint']

    # Drop all profiles first
    success = _delete_all(endpoint,
                          auth=auth,
                          params={'url:below': CANONICAL_URL})
    if not success:
        logger.error('Failed to delete existing profiles. Exiting')
        exit(1)

    # Validate profiles
    return _validate_on_server(resource_dicts, auth=auth)


def validate_resources(resource_dicts, base_url, auth=None):
    """
    Validate FHIR Resources against profiles

    Check each resource has a referenced profile in its meta.profile element
    Validate by POSTing to /<resource name>/$validate

    :param resource_dicts: list of dicts containing resources loaded from
    files
    :type resource_dicts: list of dicts
    :param base_url: FHIR server base URL
    :type base_url: str
    :param auth: basic auth parameters obj
    :type auth: requests.auth.HTTPBasicAuth
    :returns: a boolean indicating if validation was successful
    """
    # Check that each resource has a referenced profile
    for resource_dict in resource_dicts:
        file_name = os.path.split(resource_dict['file_path'])[-1]
        resource = resource_dict['content']
        profile = resource.get('meta', {}).get('profile')

        if profile is None:
            rt = resource_dict['resource_type']
            profile_uri = f'{CANONICAL_URL}/StructureDefinition/{rt}'
            display = {'meta': {'profile': profile_uri}}
            raise Exception(
                f"Profile canonical url missing in {file_name}. "
                "When validating a resource, you must specify which profile "
                f"to use via its canonical URL. You can do this by adding the "
                f"'meta' object to your resource payload. "
                f"A JSON example looks like: {pformat(display)} "
            )

        if 'endpoint' not in resource_dict:
            rt = resource_dict.get('resource_type')
            resource_dict['endpoint'] = f'{base_url}/{rt}/$validate'

    return _validate_on_server(resource_dicts, auth=auth)


def _validate_on_server(resource_dicts, auth=None):
    """
    Validate FHIR resources by POSTing them to FHIR server endpoints

    Returns whether all resources passed validation. Write results to
    validation output file located in current working directory named:
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
    results = _post_all(resource_dicts, auth=auth)

    # Write results
    if results:
        prefix = 'resource'
        if 'StructureDefinition' in resource_dicts[0]['endpoint']:
            prefix = 'profile'

        results_filepath = os.path.join(
            os.getcwd(), VALIDATION_RESULTS_FILES.get(prefix)
        )
        if os.path.isfile(results_filepath):
            os.remove(results_filepath)
        write_json(results, results_filepath)

        logger.info(f'See validation results in {results_filepath}')

    return ('errors' not in results)


def load_resources(data_path):
    """
    Read resource files from disk and create list of dicts.
    See _read_resource_file.

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :returns: a boolean indicating if validation was successful
    """
    data_path = os.path.abspath(os.path.expanduser(data_path))
    resource_dicts = []
    if not os.path.isdir(data_path):
        file_dir, file_name = os.path.split(data_path)
        file_names = [file_name]
    else:
        file_dir = data_path
        file_names = os.listdir(data_path)
    for f in file_names:
        if f in {'package.json', 'fhirpkg.lock.json'}:
            continue
        p = os.path.join(file_dir, f)
        resource = _read_resource_file(p)
        if resource:
            resource.update({'file_path': p})
            resource_dicts.append(resource)
    return resource_dicts


def _read_resource_file(filepath):
    """
    Read XML or JSON FHIR resource file into a dict:
        {
            'file_path': 'Participant.json',
            'resource_type': 'Patient',
            'content': <dict or xml.etree.ElementTree.Element>
        }

    :param filepath: path to the resource file
    :type filepath: str
    :returns: dict with resource content
    """
    logger.debug(f'Reading resource file: {filepath}')
    _, filename = os.path.split(filepath)
    file_ext = os.path.splitext(filename)[-1]
    resource_dict = None

    if file_ext == '.json':
        resource = read_json(filepath)
        resource_dict = {
            'content': resource,
            'content_type': 'json',
            'resource_type': resource.get('resourceType')
        }
    elif file_ext == '.xml':
        logger.warning('XML files not supported yet')
    else:
        logger.warning(
            f'Skipping {filename}, {file_ext} is an invalid resource file type'
        )

    return resource_dict


def _post_all(resource_dicts, auth=None):
    """
    POST FHIR resources to server and return results

    Expected form of dict in resource_dicts:

    {
        'content': <dict or xml.etree.ElementTree.Element>,
        'content_type': <xml or json>,
        'resource_type': <FHIR resource type>,
        'filepath': <path to resource source file>,
        'endpoint': <FHIR endpoint to use for validation>
    }

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
    for resource_dict in resource_dicts:
        filename = os.path.split(resource_dict['file_path'])[-1]
        resource = resource_dict['content']
        resource_type = resource_dict['resource_type']
        endpoint = resource_dict['endpoint']

        logger.info(
            f'Validating FHIR {FHIR_VERSION} {resource_type} from {filename}'
        )

        # Send post
        request_kwargs = {'auth': auth}
        request_kwargs['headers'] = {'Content-Type': 'application/json'}
        request_kwargs['json'] = resource
        success, result = _post(endpoint, **request_kwargs)

        if success:
            logger.info(f'✅ POST {filename} to {endpoint} succeeded')
            results['success'][filename] = result
        else:
            logger.info(f'❌ POST {filename} to {endpoint} failed')
            results['errors'][filename] = result

    return results


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
    try:
        resp_content = response.json()
    except json.decoder.JSONDecodeError:
        resp_content = response.text

    if response.status_code != 200:
        logger.warning(
            f'Failed to fetch existing {endpoint}. '
            f'Status code: {response.status_code}, '
            f'Caused by: {pformat(resp_content)}'
        )
        return False

    logger.debug(f'Deleting {resp_content["total"]} {endpoint} ...')
    for entry in resp_content.get('entry', []):
        if entry['resource'].get('resourceType') == 'OperationOutcome':
            continue

        resource_id = entry['resource']['id']
        logger.debug(f'Deleting {resource_id}:\n{pformat(entry)}')
        url = entry['fullUrl']
        response = requests_retry_session().delete(
            url,
            auth=request_kwargs.get('auth')
        )

        try:
            resp_content = response.json()
        except json.decoder.JSONDecodeError:
            resp_content = response.text

        if response.status_code != 204:
            logger.warning(
                f'Could not delete {url} '
                f'Status code: {response.status_code}, '
                f'Caused by: {pformat(resp_content)}'
            )
            success = False
        else:
            logger.debug(f'Deleted {url}')

    return success


def _post(endpoint, **request_kwargs):
    """
    POST a FHIR resource to the Vonk server

    :param endpoint: FHIR endpoint
    :type endpoint: str
    :param request_kwargs: optional request keyword args
    :type request_kwargs: key, value pairs
    :returns: tuple of the form (bool denoting success, response content dict)
    """
    success = False

    response = requests_retry_session().post(
        endpoint,
        **request_kwargs
    )

    try:
        resp_content = response.json()
    except json.decoder.JSONDecodeError:
        resp_content = response.text

    if response.status_code in {201, 200}:
        errors = _errors_from_response(resp_content)
        if not errors:
            success = True
            logger.debug(
                f'POST {endpoint} succeeded. '
                f'Response:\n{pformat(resp_content)}'
            )
        else:
            logger.debug(
                f'POST {endpoint} failed. Caused by:\n{pformat(resp_content)}'
            )
    else:
        logger.debug(
            f'POST {endpoint} failed, status {response.status_code}. '
            f'Caused by:\n{pformat(resp_content)}'
        )

    return success, {'status_code': response.status_code,
                     'response': resp_content}


def _errors_from_response(response_body):
    """
    Comb list of issues in Vonk response and return the ones marked error
    """
    return [issue for issue in response_body.get('issue', [])
            if issue['severity'] == 'error']
