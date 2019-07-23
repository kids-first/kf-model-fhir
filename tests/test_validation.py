import os
import logging

import pytest
from click.testing import CliRunner

from conftest import PROFILE_DIR, RESOURCE_DIR
from kf_model_fhir import cli
from kf_model_fhir.utils import read_json
from kf_model_fhir.config import VALIDATION_RESULTS_FILES


@pytest.fixture(scope='session')
def profiles():
    """
    Valid profiles for tests
    """
    runner = CliRunner()
    result = runner.invoke(
        cli.validate,
        ['profile', '--path', os.path.join(PROFILE_DIR, 'Participant.json')]
    )
    assert result.exit_code == 0


def test_validate_profiles(caplog):
    """
    Test validate profiles
    """
    caplog.set_level(logging.DEBUG)
    runner = CliRunner()
    result = runner.invoke(
        cli.validate, ['profile', '--path', PROFILE_DIR])
    assert result.exit_code != 0
    assert 'validation failed!' in caplog.text

    results_file = os.path.join(os.getcwd(),
                                VALIDATION_RESULTS_FILES.get('profile'))
    assert os.path.isfile(results_file)
    results = read_json(results_file)
    assert 'success' in results
    assert 'errors' in results

    for log_msg in [
        '✅ POST Participant.json',
        '❌ POST InvalidParticipant0.json',
        '❌ POST InvalidParticipant1.json',
        'Instance failed constraint sdf-8a',
    ]:
        assert log_msg in caplog.text


def test_validate_resources(caplog, profiles):
    """
    Test validate resources
    """
    caplog.set_level(logging.DEBUG)

    runner = CliRunner()
    result = runner.invoke(cli.validate, ['resource', '--path', RESOURCE_DIR])
    assert result.exit_code != 0
    assert 'validation failed!' in caplog.text

    for log_msg in [
        '✅ POST Participant.json',
        '❌ POST InvalidParticipant0.json',
        '❌ POST InvalidParticipant2.json',
        'Profile canonical url missing in InvalidParticipant3.json',
        'Unable to resolve reference to profile',
        "Instance count for 'Patient.gender' is 0"
    ]:
        assert log_msg in caplog.text

    assert os.path.isfile(VALIDATION_RESULTS_FILES.get('resource'))
    results = read_json(VALIDATION_RESULTS_FILES.get('resource'))
    assert 'success' in results
    assert 'errors' in results
