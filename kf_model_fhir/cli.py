"""
Entry point for the Kids First FHIR Model CLI which lets users:

- Validate FHIR model files (conformance resources, example resources)
- Convert FHIR model files between xml/json
- Push FHIR model files to FHIR server
"""
import logging

import click

from kf_model_fhir.utils import setup_logger
from kf_model_fhir import loader, app
from kf_model_fhir.config import (
    SIMPLIFIER_FHIR_SERVER_URL,
    SIMPLIFIER_USER,
    SIMPLIFIER_PW,
    FHIR_VERSION,
    DEFAULT_IG_CONTROL_FILE
)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

setup_logger()
logger = logging.getLogger(__name__)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    A CLI utility for validating FHIR Profiles and Resources
    """
    pass


@cli.command()
@click.option('--password', 'password',
              show_default=False,
              default=SIMPLIFIER_PW,
              help='Client secret or user password'
              )
@click.option('--username', 'username',
              show_default=False,
              default=SIMPLIFIER_USER,
              help='Client id or username'
              )
@click.option('--base_url', 'base_url',
              type=str,
              show_default=True,
              default=SIMPLIFIER_FHIR_SERVER_URL,
              help='URL to FHIR server where resources will be pushed'
              )
@click.argument('resource_file_or_dir',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def publish(resource_file_or_dir, base_url, username, password):
    """
    Push FHIR model files to FHIR server. Default use of this method is to
    push FHIR model files to the Simplifier FHIR server configured in
    kf_model_fhir.config

    \b
        Arguments:
            \b
            resource_dir - A directory containing the FHIR resource files to '
            'publish to the Simplifier project
    """
    try:
        app.publish_to_server(
            resource_file_or_dir, base_url, username, password
        )
    except Exception as e:
        logger.exception(str(e))
        logger.info('❌ Publish failed!')
        exit(1)
    else:
        logger.info('✅ Publish succeeded!')


@click.command()
@click.option('--publisher_opts', 'publisher_opts',
              help='A string containing command line options accepted by the '
              'IG publisher. See https://confluence.hl7.org/display/'
              'FHIR/IG+Publisher+Documentation for more details on available '
              'options. These will be passed directly to the publisher JAR'
              )
@click.option('--clear_output', 'clear_output',
              is_flag=True,
              help='Whether to clear all generated output before validating'
              )
@click.argument('ig_control_filepath',
                type=click.Path(exists=True, file_okay=True, dir_okay=False))
def validate(ig_control_filepath, clear_output, publisher_opts):
    """
    Validate FHIR conformance resources and validate example FHIR resources
    against the conformance resources by running the HL7 FHIR implementation
    guide publisher.

    See https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation

    \b
        Arguments:
            \b
            ig_control_filepath - Path to the implementation guide control
            file. The directory of this file should be the implementation guide
            site root directory containing all of the content needed to build
            the site
    """
    try:
        app.validate(ig_control_filepath, clear_output, publisher_opts)
    except Exception as e:
        logger.exception(str(e))
        logger.info('❌ Validation failed!')
        exit(1)
    else:
        logger.info('✅ Validation succeeded!')


@click.command()
@click.option('--fhir_version', 'fhir_version',
              default=FHIR_VERSION,
              show_default=True,
              help='FHIR Version')
@click.option('--format', 'format',
              type=click.Choice(['json', 'xml']),
              help='The format to convert to')
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def convert(data_path, format, fhir_version):
    """
    Convenience method to convert a FHIR resource file JSON -> XML or
    XML -> JSON and write results to a file.

    The file will have the same name and be stored in the same directory as the
    original file. It's extension will be what was provided in --format.

    \b
        Arguments:
            \b
            data_path - A directory containing the FHIR profiles or resources
            to format or a filepath to a single profile or resource.
    """

    loader.fhir_format_all(
        data_path, output_format=format, fhir_version=fhir_version
    )


@click.command()
@click.option('--ig_control_file', 'ig_control_filepath',
              help='Path to the implementation guide control file.',
              default=DEFAULT_IG_CONTROL_FILE,
              show_default=True,
              type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def add(data_path, ig_control_filepath):
    """
    Convenience method to add the necessary configuration for the resource(s)
    to the IG configuration so that the resource is included in the
    generated IG site.

    NOTE
    The resource file, `data_path`, must already be in the IG site root. This
    CLI command does not move the file into the site root.

    \b
        Arguments:
            \b
            data_path - A directory or file containing the FHIR resource
            file(s)
    """
    try:
        app.update_ig_config(data_path, ig_control_filepath)
    except Exception as e:
        logger.exception(str(e))
        logger.info(f'❌ Add {data_path} to IG failed!')
        exit(1)
    else:
        logger.info(f'✅ Add {data_path} to IG succeeded!')


cli.add_command(publish)
cli.add_command(validate)
cli.add_command(convert)
cli.add_command(add)
