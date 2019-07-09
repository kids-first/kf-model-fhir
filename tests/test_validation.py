import os
import logging

import pytest
from click.testing import CliRunner

from conftest import TEST_DATA_DIR
from kf_model_fhir import cli
from kf_model_fhir.utils import read_json
from kf_model_fhir.config import VALIDATION_RESULTS_FILES


def caplog(caplog):
    caplog.set_level(logging.DEBUG)
    return caplog


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
    Test good profiles
    """
    runner = CliRunner()
    if filename:
        data_path = os.path.join(TEST_DATA_DIR, 'profiles', filename)
    else:
        data_path = os.path.join(TEST_DATA_DIR, 'profiles')

    result = runner.invoke(cli.validate, [data_path])
    assert result.exit_code == exit_code
    assert log_msg in caplog.text

    assert os.path.isfile(VALIDATION_RESULTS_FILES.get('profile'))
    results = read_json(VALIDATION_RESULTS_FILES.get('profile'))

    if exit_code == 0:
        assert 'success' in results
        assert 'errors' not in results
    else:
        assert 'errors' in results
