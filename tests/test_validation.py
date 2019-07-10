import os
import logging

import pytest
from click.testing import CliRunner

from conftest import TEST_DATA_DIR
from kf_model_fhir import cli
from kf_model_fhir.utils import read_json
from kf_model_fhir.config import VALIDATION_RESULTS_FILES, PROJECT_DIR


@pytest.fixture(scope='function')
def caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(scope='session')
def profiles():
    runner = CliRunner()
    runner.invoke(cli.validate, ['profile', '--path',
                                 os.path.join(PROJECT_DIR, 'profiles')])


@pytest.mark.parametrize(
    'filename, exit_code, log_msg',
    [
        ('Participant.json', 0, 'Validation passed for Participant.json'),
        (None, 1, 'Validation passed for Participant.json'),
        ('InvalidParticipant0.json', 1,
         'Validation failed for InvalidParticipant0.json'),
        ('InvalidParticipant1.json', 1,
         'Validation failed for InvalidParticipant1.json')
    ])
def test_profile(caplog, filename, exit_code, log_msg):
    """
    Test profiles
    """
    runner = CliRunner()
    if filename:
        data_path = os.path.join(TEST_DATA_DIR, 'profiles', filename)
    else:
        data_path = os.path.join(TEST_DATA_DIR, 'profiles')

    result = runner.invoke(cli.validate, ['profile', '--path', data_path])
    assert result.exit_code == exit_code
    assert log_msg in caplog.text

    assert os.path.isfile(VALIDATION_RESULTS_FILES.get('profile'))
    results = read_json(VALIDATION_RESULTS_FILES.get('profile'))

    if exit_code == 0:
        assert 'success' in results
        assert 'errors' not in results
    else:
        assert 'errors' in results


@pytest.mark.parametrize(
    'filepath, exit_code, msg, expected_exc',
    [
        (os.path.join(TEST_DATA_DIR, 'resources', 'Participant.json'),
         0, 'Validation passed for Participant.json', False),
        (os.path.join(TEST_DATA_DIR, 'resources', 'InvalidParticipant0.json'),
         1,  "Instance count for 'Patient.gender' is 0", False),
        (os.path.join(TEST_DATA_DIR, 'resources', 'InvalidParticipant1.json'),
         1, 'Profile canonical url not found in InvalidParticipant1.json',
         True),
        (os.path.join(TEST_DATA_DIR, 'resources', 'InvalidParticipant2.json'),
         1, 'Unable to resolve reference to profile', False)
    ])
def test_resource(caplog, profiles, filepath, exit_code, msg, expected_exc):
    """
    Test resources
    """
    runner = CliRunner()
    result = runner.invoke(cli.validate, ['resource', '--path', filepath])
    if expected_exc:
        assert msg in str(result.exc_info)
    else:
        assert msg in caplog.text

    assert result.exit_code == exit_code

    assert os.path.isfile(VALIDATION_RESULTS_FILES.get('resource'))
    results = read_json(VALIDATION_RESULTS_FILES.get('resource'))

    if exit_code == 0:
        assert 'success' in results
        assert 'errors' not in results
    else:
        assert 'errors' in results
