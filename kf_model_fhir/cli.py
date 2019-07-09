"""
Entry point for the Kids First FHIR Model Client
"""
import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    A CLI utility for validating FHIR Profiles and Resources
    """
    pass
