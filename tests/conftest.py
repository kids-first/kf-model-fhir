import os
import logging

import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCE_DIR = os.path.join('site_root', 'input', 'resources')
TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, 'data')
FHIR_API = os.getenv('FHIR_API') or 'http://localhost:8000'
FHIR_USER = os.getenv('FHIR_USER') or 'admin'
FHIR_PW = os.getenv('FHIR_PW') or 'password'


@pytest.fixture(scope="function")
def debug_caplog(caplog):
    """
    pytest capture log output at level=DEBUG
    """
    caplog.set_level(logging.DEBUG)
    return caplog
