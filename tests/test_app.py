import os

import pytest
from click.testing import CliRunner

from ncpi_fhir_utility import cli
from conftest import (
    PROFILE_DIR,
    EXAMPLE_DIR,
    EXTENSION_DIR,
    copy_resources_into_ig
)


VALID_PROFILE_DIR = os.path.join(PROFILE_DIR, 'valid')
VALID_PROFILES = [os.path.join(VALID_PROFILE_DIR, f)
                  for f in os.listdir(VALID_PROFILE_DIR)]


@pytest.mark.parametrize(
    "dir_list, expected_code",
    [
        ([os.path.join(PROFILE_DIR, 'valid'),
          os.path.join(EXAMPLE_DIR, 'valid'),
          os.path.join(EXTENSION_DIR, 'valid')], 0),
        ([os.path.join(PROFILE_DIR, 'invalid'),
          os.path.join(EXAMPLE_DIR, 'invalid')], 1),
    ],
)
def test_ig_validation(temp_site_root, dir_list, expected_code):
    """
    Test kf_model_fhir.app.validate
    """
    runner = CliRunner()
    temp_ig_control_file = os.path.join(temp_site_root, 'ig.ini')

    # Add conformance resource and example resources to IG
    copy_resources_into_ig(dir_list, temp_site_root)

    # Validate IG
    result = runner.invoke(
        cli.validate,
        [temp_ig_control_file, '--publisher_opts', '-tx n/a', '--clear_output']
    )
    assert result.exit_code == expected_code
