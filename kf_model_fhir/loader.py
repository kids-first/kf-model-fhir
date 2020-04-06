"""
Helper module for reading resource files into Python objects and converting
XML/JSON formats
"""

import os
import json
import subprocess
import logging

from kf_model_fhir.utils import read_json, write_json
from kf_model_fhir.config import (
    TORINOX_DOCKER_REPO as DOCKER_REPO,
    FHIR_VERSION,
    TORINOX_FHIR_VERSION_MAP,
    fhir_version_name
)

logger = logging.getLogger(__name__)


def fhir_format_all(data_dir, output_format='json', fhir_version=FHIR_VERSION):
    """
    Convert all files in the directory data_path to the specified
    output format. Write each converted result to file. See fhir_format for
    more details.

    :param data_dir: directory of FHIR resource files
    :type data_dir: str
    :param output_format: Output file format, one of [json, xml]
    :type output_format: str
    """

    filepaths = path_to_valid_filepaths_list(data_dir)

    for filepath in filepaths:
        output_str, output_filepath = fhir_format(
            filepath,
            output_format=output_format,
            write_to_file=True,
            fhir_version=fhir_version
        )


def fhir_format(data_path, output_format='json', write_to_file=False,
                output_filepath=None, fhir_version=FHIR_VERSION):
    """
    Convert FHIR resource XML to JSON and vice versa.

    Optionally write the result to a file. If an output filepath is given,
    use that otherwise use the default: the file will have the same name
    and directory as the original and the new extension representing the format
    it was converted to.

    *Note*
    We cannot use one of the existing Python packages (e.g. xmltodict) to do
    the XML/JSON conversions because they're not straightforward.
    FHIR resources are structured slightly differently in each format.

    This method calls out to dockerized version of Firely's CLI tool, Torinox,
    which knows how to do conversions between FHIR XML/JSON.

    :param data_path: path to a FHIR resource file
    a single file
    :type data_path: str
    :param output_format: Output file format, one of [json, xml]
    :type output_format: str
    :param write_to_file: whether to write the converted result to file or not
    :type write_to_file: bool
    :returns: if write_to_file=True return tuple (output_str, output_filepath)
    else return output_str
    """
    dirname, file_name = os.path.split(data_path)
    file_ext = os.path.splitext(file_name)[-1]

    logger.info(
        f'Converting content of {file_ext} file {data_path} to '
        f'{output_format} format ... '
    )

    # Do FHIR format conversion
    TAG, APP = TORINOX_FHIR_VERSION_MAP.get(fhir_version_name(FHIR_VERSION))
    cmd_str = (
        f'docker run --rm -v {dirname}:/fhir_data {DOCKER_REPO}:{TAG} '
        f'{APP} show /fhir_data/{file_name} --{output_format}'
    )
    logger.debug(f'Using {cmd_str}')
    output = subprocess.run(cmd_str, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    output_str = output.stdout.decode('utf-8')
    if output.returncode != 0:
        raise Exception(
            f'Could not convert {file_ext} file {data_path} to '
            f'{output_format} file! Caused by \n\n{output_str}'
        )

    logger.debug(f'Converted content:{output_str}')

    # Write output
    if write_to_file:
        if not output_filepath:
            output_filepath = os.path.join(
                dirname, os.path.splitext(file_name)[0] + f'.{output_format}'
            )
        # Don't overwrite existing files
        if os.path.isfile(output_filepath):
            raise FileExistsError(
                f'Convert {file_ext} file {data_path} to '
                f'{output_format} failed! The file {output_filepath} '
                'already exists!'
            )
        if output_format == 'json':
            write_json(json.loads(output_str), output_filepath,
                       sort_keys=False)
        else:
            with open(output_filepath, 'w') as xml_file:
                xml_file.write(output_str)

        logger.info(f'Converted content written to {output_filepath}')

        return output_str, output_filepath
    else:
        return output_str


def load_resources(data_path):
    """
    Read resource files from disk and create list of dicts containing
    resource file content and metadata. See _read_resource_file.

    :param data_path: directory or file path to the resource file(s)
    :type data_path: str
    :param resource_type: one of [profile | resource]
    :type resource_type: str

    :returns: dict of resource dicts keyed by resource file path
    """
    filepaths = path_to_valid_filepaths_list(data_path)
    resource_dicts = []
    for p in filepaths:
        resource_dict = read_resource_file(p)
        if resource_dict:
            resource_dicts.append(resource_dict)

    return resource_dicts


def read_resource_file(filepath):
    """
    Read XML or JSON FHIR resource file into a dict of the form:
        {
            'filename': 'Participant.json',
            'filepath': '/project/profiles/Participant.json',
            'resource_type': 'Patient',
            'content': dict,
            'content_type': json
        }

    XML file content will be converted to a JSON string and then loaded
    into a Python dict similar to how JSON files are loaded.

    :param filepath: path to the resource file
    :type filepath: str
    :returns: dict with resource content and metadata
    """
    logger.debug(f'Reading resource file: {filepath}')

    _, filename = os.path.split(filepath)
    file_ext = os.path.splitext(filename)[-1]
    resource_dict = None

    if file_ext == '.json':
        resource = read_json(filepath)

    elif file_ext == '.xml':
        resource_json_str = fhir_format(filepath,
                                        output_format='json',
                                        write_to_file=False)
        resource = json.loads(resource_json_str)

    if file_ext in {'.json', '.xml'}:
        resource_dict = {
            'filepath': filepath,
            'filename': filename,
            'content': resource,
            'content_type': 'json',
            'resource_type': resource.get('resourceType')
        }
    else:
        logger.warning(
            f'Skipping "{filename}", {file_ext} is an invalid resource '
            'file type'
        )

    return resource_dict


def path_to_valid_filepaths_list(data_path):
    """
    Make list of valid filepaths from data_path which could be a directory
    or a filepath.

    :param data_path: path to directory or file
    :type data_path: str
    :returns: list of file paths
    """
    data_path = os.path.abspath(os.path.expanduser(data_path))
    filepaths = []
    if os.path.isdir(data_path):
        for root, dirs, files in os.walk(data_path):
            for f in files:
                fn, ext = os.path.splitext(f)
                if (
                    (f not in {'package.json', 'fhirpkg.lock.json'}) and
                    (ext in {'.xml', '.json'})
                ):
                    filepaths.append(os.path.join(root, f))

    else:
        filepaths = [data_path]

    return filepaths
