"""
Entry point for the Kids First FHIR Model Client
"""
import logging
import os

import click

from kf_model_fhir.utils import setup_logger, check_service_status
from kf_model_fhir.config import SERVER_BASE_URL, PROJECT_DIR
from kf_model_fhir import app

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
                  f'\n`{PROJECT_DIR}/profiles` if resource_type=profile or '
                  f'\n`{PROJECT_DIR}/resources` if resource_type=resource'
              ))
@click.argument('resource_type',
                type=click.Choice(['profile', 'resource']))
def validate(resource_type, data_path):
    """
    Validate FHIR Profiles or example FHIR Resources against the Profiles

    \b
        Arguments:
            \b
            resource_type - Must be one of {profile, resource}
    """
    # Check service status
    if check_service_status(SERVER_BASE_URL):
        logger.error(f'FHIR validation server {SERVER_BASE_URL} must be '
                     'up in order to continue with validation')
        exit(1)

    if not data_path:
        data_path = os.path.join(PROJECT_DIR, resource_type + 's')

    if resource_type == 'profile':
        success = app.validate_profiles(data_path)
    else:
        success = app.validate_resources(data_path)

    if not success:
        logger.error(f'❌ {resource_type.title()} validation failed!')
        exit(1)
    else:
        logger.info(f'✅ {resource_type.title()} validation passed!')


cli.add_command(validate)
