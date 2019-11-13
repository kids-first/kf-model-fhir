"""
Entry point for the Kids First FHIR Model Client
"""
import logging

import click

from kf_model_fhir.utils import (
    setup_logger
)
from kf_model_fhir.config import (
    PROFILE_DIR,
    RESOURCE_DIR,
    SERVER_CONFIG
)
from kf_model_fhir.validation import FhirValidator
from kf_model_fhir import app, loader

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

setup_logger()
logger = logging.getLogger(__name__)

CONF_RESOURCE_TYPES = {'extension', 'search_parameter'}


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    A CLI utility for validating FHIR Profiles and Resources
    """
    pass


@click.command()
@click.option(
    '--exclude', '-e', multiple=True,
    help='The type of conformance resources to exclude. Must be one of '
         f'{CONF_RESOURCE_TYPES}',
    type=click.Choice(CONF_RESOURCE_TYPES)
)
@click.option('--server_name', 'server_name',
              help='Name of server',
              type=click.Choice(list(SERVER_CONFIG.keys()))
              )
@click.option('--password', 'password',
              help='Client secret or user password'
              )
@click.option('--username', 'username',
              help='Client id or username'
              )
@click.option('--path', 'data_path',
              type=click.Path(exists=True, file_okay=True, dir_okay=True),
              help=(
                  'A directory containing the FHIR profiles or resources to '
                  'validate or a filepath to a single profile or resource. '
                  'If not provided, defaults to:'
                  f'\n`{PROFILE_DIR}` if resource_type=profile or '
                  f'\n`{RESOURCE_DIR}` if resource_type=resource'
              ))
@click.argument('resource_type',
                type=click.Choice(['profile', 'resource']))
def validate(resource_type, data_path, username, password, server_name,
             exclude):
    """
    Validate FHIR Profiles or example FHIR Resources against the Profiles.

    If extension type profiles exist then they will be validated before other
    profiles are validated. Extensions should be placed in a subdirectory of
    --path, called `extensions`.'

    \b
        Arguments:
            \b
            resource_type - Must be one of {profile, resource}
    """
    success = FhirValidator(
        server_cfg=SERVER_CONFIG.get(server_name),
        username=username,
        password=password).validate(resource_type, data_path,
                                    exclude=exclude),
    if not success:
        exit(1)


@cli.command()
@click.option(
    '--exclude', '-e', multiple=True,
    help='The type of conformance resources to exclude. Must be one of '
         f'{CONF_RESOURCE_TYPES}',
    type=click.Choice(CONF_RESOURCE_TYPES)
)
@click.option('--server_name', 'server_name',
              help='Name of server',
              type=click.Choice(list(SERVER_CONFIG.keys()))
              )
@click.option('--project', 'project',
              help='Simplifier.net project to publish to'
              )
@click.option('--password', 'password',
              help='Client secret or user password'
              )
@click.option('--username', 'username',
              help='Client id or username'
              )
@click.option('--resource_type', 'resource_type',
              type=click.Choice(['resource', 'profile']),
              default='profile',
              show_default=True,
              help='The type of thing to publish'
              )
@click.argument('resource_dir',
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def publish(resource_dir, resource_type, username, password, project,
            server_name, exclude):
    """
    Push FHIR model files to Simplifier project

    \b
        Arguments:
            \b
            resource_dir - A directory containing the FHIR resource files to '
            'publish to the Simplifier project
    """
    success = app.publish_to_server(
        resource_dir, resource_type, username, password, project,
        server_name, exclude
    )
    if not success:
        logger.error(f'❌ Publish {resource_type.lower()} files failed!')
        exit(1)
    else:
        logger.info(f'✅ Publish {resource_type.lower()} files succeeded!')


@click.command()
@click.option('--format', 'format',
              type=click.Choice(['json', 'xml']),
              help='The format to convert to')
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def convert(data_path, format):
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

    loader.fhir_format_all(data_path, output_format=format)


@click.command()
@click.option('--patients', 'patients',
              type=int,
              default=10,
              show_default=True,
              help='# of patients to generate')
@click.argument('resource_dir',
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def generate(resource_dir, patients=10):
    app.generate(resource_dir, patients=patients)


cli.add_command(convert)
cli.add_command(publish)
cli.add_command(validate)
cli.add_command(generate)
