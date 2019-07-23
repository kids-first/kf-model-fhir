"""
Entry point for the Kids First FHIR Model Client
"""
import logging
import os
from pprint import pformat

import click

from kf_model_fhir.utils import (
    setup_logger,
    settings_diff
)
from kf_model_fhir.config import (
    PROFILE_DIR,
    RESOURCE_DIR,
    ROOT_DIR
)
from kf_model_fhir.validation import FhirValidator
from kf_model_fhir import app, loader

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

setup_logger()
logger = logging.getLogger(__name__)


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    A CLI utility for validating FHIR Profiles and Resources
    """
    pass


@click.command()
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
def validate(resource_type, data_path):
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
    success = FhirValidator().validate(resource_type, data_path)
    if not success:
        exit(1)


@cli.command()
def generate_settings():
    """
    Generate server settings .env files from the corresponding JSON
    settings files

    To control server settings, users should modify:
        ../server/appsettings.json
        ../server/logsettings.json

    and then run this command to generate the .env files containing the
    settings that changed from the defaults.

    The .env files are referenced by the docker-compose.yml file which
    passes the settings as environment variables to the server container
    on docker-compose up command.
    """
    # App settings and log settings
    for settings in ['appsettings', 'logsettings']:
        fp = os.path.join(ROOT_DIR, 'server', f'{settings}.json')
        dfp = os.path.join(ROOT_DIR, 'server', f'{settings}.default.json')
        output_filepath = os.path.join(ROOT_DIR, 'server', f'{settings}.env')
        logger.info(f'Updating server {settings}: {output_filepath}, '
                    f'using {fp}')

        var_prefix = 'VONK_'
        if 'log' in settings:
            var_prefix = 'VONKLOG_'

        changed = settings_diff(fp, dfp, var_prefix=var_prefix)

        logger.info(f'Detected changes from defaults:\n{pformat(changed)}')

        with open(output_filepath, 'w') as settings_file:
            settings_file.write('\n'.join(changed))

        logger.info(f'Updated server {settings}: {output_filepath}')


@cli.command()
@click.option('--project', 'project',
              help='Simplifier.net project to publish to'
              )
@click.option('--password', 'password',
              help='Simplifier.net password'
              )
@click.option('--username', 'username',
              help='Simplifier.net username'
              )
@click.option('--resource_type', 'resource_type',
              type=click.Choice(['resource', 'profile']),
              default='profile',
              show_default=True,
              help='The type of thing to publish'
              )
@click.argument('resource_dir',
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def publish(resource_dir, resource_type, username, password, project):
    """
    Push FHIR model files to Simplifier project

    \b
        Arguments:
            \b
            resource_dir - A directory containing the FHIR resource files to '
            'publish to the Simplifier project
    """
    success = app.publish_to_simplifier(
        resource_dir, resource_type, username, password, project
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


cli.add_command(convert)
cli.add_command(publish)
cli.add_command(generate_settings)
cli.add_command(validate)
