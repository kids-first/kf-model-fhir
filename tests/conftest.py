import os
import shutil

import pytest

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, 'data')
PROFILE_DIR = os.path.join(TEST_DATA_DIR, 'profiles')
EXTENSION_DIR = os.path.join(TEST_DATA_DIR, 'extensions')
EXAMPLE_DIR = os.path.join(TEST_DATA_DIR, 'examples')
TEST_SITE_ROOT = os.path.join(TEST_DATA_DIR, 'site_root')
TEST_IG_CONTROL_FILE = os.path.join(TEST_SITE_ROOT, 'ig.ini')


@pytest.fixture(scope='function')
def temp_site_root(tmpdir):
    """
    Temp ig for tests
    """
    temp = tmpdir.mkdir('temp')
    temp_site_root = os.path.join(temp, 'site_root')

    # Copy source for IG
    shutil.copytree(TEST_SITE_ROOT, temp_site_root)

    return temp_site_root
