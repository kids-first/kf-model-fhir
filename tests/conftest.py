import os
import shutil
import logging

import pytest

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, 'data')
PROFILE_DIR = os.path.join(TEST_DATA_DIR, 'profiles')
EXTENSION_DIR = os.path.join(TEST_DATA_DIR, 'extensions')
EXAMPLE_DIR = os.path.join(TEST_DATA_DIR, 'examples')
TEST_SITE_ROOT = os.path.join(TEST_DATA_DIR, 'site_root')
TEST_IG_CONTROL_FILE = os.path.join(TEST_SITE_ROOT, 'ig.ini')

INVALID_RESOURCES = [
    ({'content':
      {
          'resourceType': 'StructureDefinition',
          'url': 'http://foo.org/participant'
      },
      'filepath': 'StructureDefinition-participant.json'
      }, 'All resources must have an `id` attribute'),
    ({'content':
      {
          'resourceType': 'StructureDefinition',
          'id': 'participant',
          'url': 'http://foo.org/foo'
      },
      'filepath': '/StructureDefinition-participant.json'
      }, 'Invalid value for `url`'),
    ({'content':
      {
          'resourceType': 'StructureDefinition',
          'id': 'participant',
      },
      'filepath': '/StructureDefinition-participant.json'
      }, 'All StructureDefinition resources must have a `url`'),
    ({'content':
      {
          'resourceType': 'StructureDefinition',
          'id': 'Participant',
          'url': 'http://foo.org/Participant'
      },
      'filepath': '/StructureDefinition-Participant.json'
      }, 'Resource id must adhere to kebab-case'),
    ({'content':
      {
          'resourceType': 'StructureDefinition',
          'id': 'participant',
          'url': 'http://foo.org/participant'
      },
      'filepath': '/StructureDefinition-biospecimen.json'
      }, 'Resource file names must follow pattern')

]


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


@pytest.fixture(scope="function")
def debug_caplog(caplog):
    """
    pytest capture log output at level=DEBUG
    """
    caplog.set_level(logging.DEBUG)
    return caplog
