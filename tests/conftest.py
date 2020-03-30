import os
import shutil
import pytest

from kf_model_fhir import app
from kf_model_fhir.config import DEFAULT_SITE_ROOT, DEFAULT_IG_CONTROL_FILE

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, 'data')
PROFILE_DIR = os.path.join(TEST_DATA_DIR, 'profiles')
EXTENSION_DIR = os.path.join(TEST_DATA_DIR, 'extensions')
EXAMPLE_DIR = os.path.join(TEST_DATA_DIR, 'examples')


@pytest.fixture(scope='function')
def temp_ig(tmpdir):
    """
    Test kf_model_fhir.app.add_resource_to_ig
    """
    temp = tmpdir.mkdir('temp')
    temp_site_root = os.path.join(temp, 'site_root')

    # Clear generated outputs
    app.clear_ig_output(DEFAULT_IG_CONTROL_FILE)

    # Copy source for IG
    shutil.copytree(DEFAULT_SITE_ROOT, temp_site_root)

    return temp_site_root
