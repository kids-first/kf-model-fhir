"""
General module for methods called by the kf_model_fhir.cli
    - Validation of FHIR data model using IG publisher
    - Add resource configuration to IG files
    - Publish FHIR data model (conformance and example resources)
      to Simplifier.net
"""
import os
import logging
import subprocess
from shutil import rmtree

from requests.auth import HTTPBasicAuth

from kf_model_fhir import loader
from kf_model_fhir.client import FhirApiClient
from kf_model_fhir.utils import read_json, write_json
from kf_model_fhir.config import (
    RUN_IG_PUBLISHER_SCRIPT,
    CONFORMANCE_RESOURCES
)

FILE_NAME_DELIMITER = '_'
logger = logging.getLogger(__name__)


def validate(ig_control_filepath, clear_output=False,
             publisher_opts=''):
    """
    Validate the FHIR data model (FHIR conformance and example resources)

    Run the HL7 FHIR implementation guide (IG) publisher in a Docker container
    to validate conformance resources and any example resources against the
    conformance resources.

    See https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation

    Validation fails if the publisher returns a non-zero exit code or if
    the QA report contains errors with the FHIR resources.

    IG build errors are ignored since this method only validates the data
    model

    :param ig_control_filepath: Path to the implementation guide control file
    :type ig_control_filepath: str
    :param clear_output: Whether to clear all generated output before
    validating
    :type clear_output: boolean
    :param publisher_opts: IG publisher command line options forwarded directly
    to the publisher CLI
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
    ig_control_filepath = os.path.abspath(
        os.path.expanduser(ig_control_filepath)
    )
    args = [RUN_IG_PUBLISHER_SCRIPT, ig_control_filepath]
    if publisher_opts:
        args.append(publisher_opts)
    subprocess.run(args, shell=False, check=True)

    # Check QA report for validation errors
    qa_path = os.path.join(
        site_root, output_paths.get('output', ''), 'qa'
    )
    qa_report = os.path.abspath(qa_path + '.html')
    logger.info(f'Checking QA report {qa_report} for validation errors')
    qa_json = read_json(qa_path + '.json')
    if qa_json.get('errs'):
        raise Exception(
            f'Errors found in QA report. See {qa_report}'
        )

    logger.info('End validation of FHIR data model')


def get_ig_output_dirs(ig_control_filepath):
    """
    Read in IG control file to determine which output dirs
    were generated by IG publisher

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


def add_resource_to_ig(resource_filepath, ig_control_filepath,
                       is_example=False, markdown_dirpath=None):
    """
    Add the necessary configuration for the resource to the IG site root
    so that it is included in the generated IG site.

    When a new resource file is added to the IG it will not be picked up for
    validation or site generation by the IG publisher unless the expected
    configuration for that resource is present.

    This method does the following:

    1. Adds entry for the resource to IG control file
    2. Adds entry for the resource to IG resource file
    3. If a conformance resource, creates markdown placeholder file in
       <IG site root>/source/pages/_includes

    :param resource_filepath: Path to the FHIR resource file
    :type resource_filepath: str
    :param ig_control_filepath: Path to the implementation guide control file
    :type ig_control_filepath: str
    :param is_example: Whether this is an example resource or
    conformance resource
    :type is_example: bool
    """
    site_root = os.path.dirname(ig_control_filepath)

    # Load resource from file
    resource_dict = loader.load_resources(resource_filepath)[0]
    content = resource_dict['content']
    r_type = content.get('resourceType')
    r_id = content.get('id')

    # Read in IG control file
    ig_config = read_json(os.path.abspath(
        os.path.expanduser(ig_control_filepath)
    ))

    # --- Add resource entry to IG control file ---
    file = os.path.split(resource_filepath)[-1]

    # Get resource id
    if not r_id:
        raise KeyError(
            'All resources must have a defined `id`! '
            f'`id` = {r_id} in {resource_filepath}'
        )

    # Conformance resource
    if r_type in CONFORMANCE_RESOURCES:
        r_base = content.get('baseDefinition').split('/')[-1]
        file_prefix = FILE_NAME_DELIMITER.join([r_type, r_base, r_id])
        entry = {
            f"{r_type}/{r_id}": {
                "source": file,
                "base": f"{file_prefix}.html",
                "defns": f"{file_prefix}-definitions.html"
            }
        }
    # Example resource
    else:
        r_base = content.get('meta', {}).get('profile', [None])[0]
        if r_base is None:
            r_base = r_type
        else:
            r_base = r_base.split('/')[-1]

        file_prefix = FILE_NAME_DELIMITER.join([r_type, r_base, r_id])

        entry = {
            f"{r_type}/{r_id}": {
                "source": f"{file}",
                "base": f"{file_prefix}.html"
            }
        }
    ig_config['resources'].update(entry)
    write_json(ig_config, ig_control_filepath)

    # --- Add resource entry to IG resource file ---
    # Read in the IG resource, but first find where it is
    for subdir in ig_config['paths']['resources']:
        ig_resource_fp = os.path.join(site_root, subdir, ig_config['source'])
        if os.path.exists(ig_resource_fp):
            break
    ig_resource = read_json(ig_resource_fp)

    # Add resource to IG resource payload
    references_dict = {
        ref['reference']['reference']: ref
        for ref in ig_resource['definition']['resource']
    }
    ref_id = f"{r_type}/{r_id}"
    references_dict[ref_id] = {
        'reference': {
            'reference': f"{r_type}/{r_id}",
            'display': f"{file_prefix.replace(FILE_NAME_DELIMITER, ' ')}"
        },
        'exampleBoolean': is_example
    }
    ig_resource['definition']['resource'] = list(references_dict.values())
    write_json(ig_resource, ig_resource_fp)

    # Add conformance resource markdown
    if r_type in CONFORMANCE_RESOURCES:
        markdown_dir = markdown_dirpath or os.path.join(
            site_root, 'source', 'pages', '_includes')
        for f in ['intro', 'summary', 'search']:
            fp = os.path.join(markdown_dir, f'{r_id}-{f}.md')
            with open(fp, 'w') as markdown_file:
                markdown_file.write(f'Put {r_id} {f.title()} here')
                if f == 'intro':
                    markdown_file.write(
                        f'\n\n[Example {r_id}](replace-me.html)'
                    )


def publish_to_server(resource_file_or_dir, base_url, username=None,
                      password=None, fhir_version=None):
    """
    Push FHIR resources to a FHIR server

    Delete the resources if they exist on the server
    PUT any resources that have an `id` attribute defined
    POST any resources that do not have an `id` attribute defined

    :param resource_file_or_dir: path to a directory containing FHIR resource
    files or path to a single resource file
    :type resource_file_or_dir: str
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
        f'Begin publishing resources in {resource_file_or_dir} to {base_url}'
    )
    if username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        auth = None

    client = FhirApiClient(
        base_url=base_url, auth=auth, fhir_version=fhir_version
    )
    resources = loader.load_resources(resource_file_or_dir)

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
