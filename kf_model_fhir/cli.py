"""
Entry point for the Kids First FHIR Model Client
"""
import logging

import click

from kf_model_fhir.utils import setup_logger
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
@click.option('--type', 'resource_type',
              type=click.Choice(['profile', 'resource']),
              default='profile',
              show_default=True,
              help=('The type of FHIR thing we are validating'))
@click.argument('data_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=True))
def validate(data_path, resource_type):
    """
    Validate FHIR Profiles or example FHIR Resources against the Profiles

    \b
        Arguments:
            \b
            path - A directory containing the FHIR profiles or resources to
            validate or a filepath to a single profile or resource
    """
    success = app.validate(data_path, resource_type)
    if not success:
        logger.error(f'❌ {resource_type.title()} validation failed!')
        exit(1)
    else:
        logger.info(f'✅ {resource_type.title()} validation passed!')


cli.add_command(validate)
