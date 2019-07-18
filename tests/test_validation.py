import os
import logging

import pytest
from click.testing import CliRunner

from conftest import PROFILE_DIR, RESOURCE_DIR
from kf_model_fhir import cli
from kf_model_fhir.utils import read_json, write_json
from kf_model_fhir.config import VALIDATION_RESULTS_FILES, PROJECT_DIR


@pytest.fixture(scope='session')
def profiles():
    runner = CliRunner()
    runner.invoke(cli.validate, ['profile', '--path',
                                 os.path.join(PROJECT_DIR, 'profiles')])


def test_profiles(caplog):
    """
    Test profiles
    """
    caplog.set_level(logging.DEBUG)
    runner = CliRunner()
    result = runner.invoke(cli.validate, ['profile', '--path', PROFILE_DIR])
    assert result.exit_code != 0
    assert 'validation failed!' in caplog.text

    results_file = os.path.join(os.getcwd(),
                                VALIDATION_RESULTS_FILES.get('profile'))
    assert os.path.isfile(results_file)
    results = read_json(results_file)
    assert 'errors' in results

    for log_msg in ['✅ POST Participant.json',
                    '✅ POST Participant.xml',
                    '❌ POST InvalidParticipant0.json',
                    '❌ POST InvalidParticipant1.json']:
        assert log_msg in caplog.text


def test_resource(profiles, caplog):
    """
    Test resources
    """
    caplog.set_level(logging.DEBUG)

    runner = CliRunner()
    result = runner.invoke(cli.validate, ['resource', '--path', RESOURCE_DIR])
    assert result.exit_code != 0
    assert 'validation failed!' in caplog.text

    for log_msg in [
        '✅ POST Participant.json',
        '✅ POST Participant.xml',
        "Instance count for 'Patient.gender' is 0"
    ]:
        assert log_msg in caplog.text

    assert os.path.isfile(VALIDATION_RESULTS_FILES.get('resource'))
    results = read_json(VALIDATION_RESULTS_FILES.get('resource'))
    assert 'errors' in results


def test_resource_bad_prof_references(tmpdir, caplog):
    """
    Test resources with bad/missing references to profiles
    """
    # Bad profile reference
    content = {
        "resourceType": "Patient",
        "gender": "female",
        "meta": {
            "profile": "http://fhirstu3.kids-first.io/fhir/StructureDefinition/oqweurpiouajfa;lk@#"
        },

        "name": [
            {
                "family": "Singh"
            }
        ]
    }
    fp = os.path.join(tmpdir, 'bad_resource.json')
    write_json(content, fp)
    runner = CliRunner()
    result = runner.invoke(cli.validate, ['resource', '--path', fp])
    assert result.exit_code != 0
    assert 'Unable to resolve reference to profile' in caplog.text

    # Missing profile reference
    content['meta'].pop('profile')
    write_json(content, fp)
    runner = CliRunner()
    result = runner.invoke(cli.validate, ['resource', '--path', fp])
    assert result.exit_code != 0
    assert 'Profile canonical url missing' in str(result.exc_info)
