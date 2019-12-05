"""
General module for methods called by the kf_model_fhir.cli
    - Validation of FHIR data model using IG publisher
    - Publish FHIR data model (resources and docs) to Simplifier.net
"""
import os
import logging
import subprocess
from shutil import rmtree

from requests.auth import HTTPBasicAuth

from kf_model_fhir import loader
from kf_model_fhir.client import FhirApiClient
from kf_model_fhir.utils import read_json
from kf_model_fhir.config import (
    RUN_IG_PUBLISHER_SCRIPT
)

logger = logging.getLogger(__name__)


def validate(ig_control_filepath, clear_output=True,
             publisher_opts=''):
    """
    Validate the FHIR data model (FHIR conformance and example resources)

    Run the HL7 FHIR implementation guide (IG) publisher in a Docker container
    to validate conformance resources and any example resources against the
    conformance resources.
    See https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation

    Validation fails if the publisher returned a non-zero exit code or if
    the QA report contains errors with the FHIR resources.

    IG build errors are ignored since this method only validates the data
    model

    :param ig_control_filepath: Path to the implementation guide control file
    :type ig_control_filepath: str
    :param clear_output: Whether to clear all generated output before
    validating
    :type clear_output: boolean
    :param publisher_opts: IG publisher command line options
    :type publisher_opts: str
    """
    logger.info('Begin validation of FHIR data model')
    site_root = os.path.dirname(ig_control_filepath)

    # Clear previously generated output
    if clear_output:
        output_paths = clear_ig_output(ig_control_filepath)
    else:
        output_paths = get_ig_output_dirs(ig_control_filepath)

    # Run IG publisher
    cmd_str = (
        f'{RUN_IG_PUBLISHER_SCRIPT} {ig_control_filepath}'
    )
    if publisher_opts:
        cmd_str = f'{cmd_str} {publisher_opts}'
    subprocess.run(cmd_str, shell=True, check=True)

    # Check QA report for validation errors
    qa_path = os.path.join(
        site_root, output_paths.get('output', ''), 'qa'
    )
    qa_report = qa_path + '.html'
    logger.info(f'Checking QA report {qa_report} for validation errors')
    with open(qa_path + '.txt', 'r') as qa_txt:
        lines = qa_txt.readlines()
        summary = lines[3]
        errors = summary.split(',')[0].strip().split('=')[-1].strip()
        if int(errors) > 0:
            raise Exception(
                f'Errors found in QA report. See {qa_report}'
            )

    logger.info('End validation of FHIR data model')


def get_ig_output_dirs(ig_control_filepath):
    """
    Read in IG control file to determine output dirs generated by IG publisher

    :param ig_control_filepath: Path to the implementation guide control file
    :type ig_control_filepath: str
    """
    config = read_json(ig_control_filepath)
    default_dirs = ['qa', 'temp', 'output', 'txCache']
    output_paths = {}
    for k in default_dirs:
        v = config.get('paths', {}).get(k, k)
        output_paths[k] = v
    return output_paths


def clear_ig_output(ig_control_filepath):
    """
    Delete all of the output dirs generated by the IG publisher

    :param ig_control_filepath: Path to the implementation guide control file
    :type ig_control_filepath: str
    """
    site_root = os.path.dirname(ig_control_filepath)
    output_paths = get_ig_output_dirs(ig_control_filepath)
    for k, rel_path in output_paths.items():
        p = os.path.join(site_root, rel_path)
        if os.path.exists(p):
            logger.info(
                f'Clearing all previously generated output at: {p}'
            )
            rmtree(p)

    return output_paths


def publish_to_server(resource_dir, base_url, username=None, password=None,
                      fhir_version=None):
    """
    Push FHIR resources to server

    Delete the resources if they exist on the server
    PUT any resources that have an `id` attribute defined
    POST any resources that do not have an `id` attribute defined

    :param resource_dir: directory containing FHIR resource files
    :type resource_dir: str
    :param resource_type: directory containing FHIR resource files
    :type resource_type: str
    :param username: Server account username
    :type username: str
    :param password: Server account password
    :type password: str
    :param fhir_version: FHIR version number
    :type fhir_version: str
    """
    logger.info(
        f'Begin publishing resources in {resource_dir} to {base_url}'
    )
    if username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        auth = None

    client = FhirApiClient(
        base_url=base_url, auth=auth, fhir_version=fhir_version
    )
    resources = loader.load_resources(resource_dir)

    # Delete existing resources
    for r_dict in resources:
        r = r_dict['content']
        if 'url' in r:
            success = client.delete_all(
                f'{base_url}/{r["resourceType"]}', params={'url': r['url']}
            )
        elif 'id' in r:
            success, results = client.send_request(
                'delete',
                f'{base_url}/{r["resourceType"]}/{r["id"]}'
            )
        else:
            logger.warning(
                f'⚠️ Could not delete {r_dict["filename"]}. No way to '
                'identify the resource. Tried looking for `url` and `id` in '
                'payload.'
            )

    # POST if no id is provided, PUT if id is provided
    for r_dict in resources:
        r = r_dict['content']
        id_ = r.get('id')
        if id_:
            success, results = client.send_request(
                'put',
                f'{base_url}/{r["resourceType"]}/{id_}',
                json=r
            )
        else:
            success, results = client.send_request(
                'post',
                f'{base_url}/{r["resourceType"]}',
                json=r
            )
