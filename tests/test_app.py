import os

import pytest
from click.testing import CliRunner
from conftest import (
    RESOURCE_DIR,
    FHIR_API,
    FHIR_USER,
    FHIR_PW
)

from ncpi_fhir_utility import cli
from ncpi_fhir_utility.client import FhirApiClient


@pytest.mark.parametrize(
    "resource_dir",
    [
        (os.path.join(RESOURCE_DIR, 'terminology')),
        (os.path.join(RESOURCE_DIR, 'extensions')),
        (os.path.join(RESOURCE_DIR, 'profiles')),
        (os.path.join(RESOURCE_DIR, 'search')),
        # TODO - This fails because we don't have the external terminology
        # server setup with our integration test server.
        # Once that is complete, then uncomment the line below
        # (os.path.join(RESOURCE_DIR, 'examples'),
    ]
)
def test_deploy_model(resource_dir):
    """
    Test loading the FHIR model into the integration test server

    Order of load: terminology, extensions, profiles, search parameters,
    example resources.
    """
    runner = CliRunner()
    result = runner.invoke(
        cli.publish,
        [resource_dir, '--base_url', FHIR_API,
         '--username', FHIR_USER, '--password', FHIR_PW]
    )
    assert result.exit_code == 0


def test_ingest_plugin():
    # Instantiate LoadStage with kf-model-fhir/ingest_plugin/kids_first_fhir.py
    # Read test data TSVs
    pass


def test_search_params():
    pass
