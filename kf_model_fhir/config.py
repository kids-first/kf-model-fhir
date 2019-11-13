import logging
import os


def fhir_version_name(fhir_version):
    """
    Get the name of a particular FHIR version number

    :param: fhir_version
    :type: str

    :returns: str
    """
    major_version = int(fhir_version.split('.')[0])

    if major_version < 3:
        return 'dstu2'
    elif (major_version >= 3) and (major_version < 4):
        return 'stu3'
    elif (major_version >= 4) and (major_version < 5):
        return 'r4'
    else:
        raise Exception(
            f'Invalid fhir version supplied: {fhir_version}! No name exists '
            'for the supplied fhir version.'
        )


DEFAULT_LOG_LEVEL = logging.DEBUG

FHIR_VERSION = '4.0.0'
FHIR_VERSION_NAME = fhir_version_name(FHIR_VERSION)

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, 'project')
PROFILE_DIR = os.path.join(PROJECT_DIR, 'profiles')
RESOURCE_DIR = os.path.join(PROJECT_DIR, 'resources')
EXTENSION_DIR = os.path.join(PROFILE_DIR, 'extensions')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
TORINOX = '~/.dotnet/tools/fhir'
VALIDATE_PROFILE_SH = os.path.join(SCRIPTS_DIR, 'torinox_validate_profile.sh')
VALIDATION_RESULTS_FILES = {'profile': 'profile_validation_results.json',
                            'resource': 'resource_validation_results.json'}

SIMPLIFIER_USER = os.environ.get('SIMPLIFIER_USER')
SIMPLIFIER_PW = os.environ.get('SIMPLIFIER_PW')
SIMPLIFIER_PROJECT_NAME = 'KidsFirstR4'
SIMPLIFIER_FHIR_SERVER_URL = 'https://fhir.simplifier.net'


CANONICAL_URL = f'http://fhir{FHIR_VERSION_NAME}.kids-first.io/fhir'
TORINOX_DOCKER_REPO = 'kidsfirstdrc/torinox'
TORINOX_DOCKER_IMAGE_TAG = 'torinox-1.0.2'

SERVER_CONFIG = {
    'aidbox': {
        'base_url': 'http://localhost:8081/fhir',
        'status_url': 'http://localhost:8081',
        'endpoints': {
            'StructureDefinition': 'StructureDefinition',
            'search_parameter': 'SearchParameter'
        },
        'username': 'root',
        'password': 'secret'
    },
    'vonk': {
        'base_url': 'http://localhost:8080',
        'endpoints': {
            'StructureDefinition': 'administration/StructureDefinition',
            'SearchParameter': 'administration/SearchParameter'
        }
    },
    'smile-cdr': {
        'base_url': 'https://try.smilecdr.com:8000',
        'status_url': 'https://try.smilecdr.com:8000/metadata',
        'endpoints': {
            'StructureDefinition': 'StructureDefinition',
            'SearchParameter': 'SearchParameter'
        }
    },
    'hapi': {
        'base_url': 'http://hapi.fhir.org/baseR4',
        'status_url': 'http://hapi.fhir.org/baseR4/metadata',
        'endpoints': {
            'StructureDefinition': 'StructureDefinition',
            'SearchParameter': 'SearchParameter'
        }
    },
    'azure': {
        'base_url': 'https://kids-first-fhir-service.azurewebsites.net',
        'endpoints': {
            'StructureDefinition': 'StructureDefinition',
            'SearchParameter': 'SearchParameter'
        }
    },
    'simplifier': {
        'base_url': SIMPLIFIER_FHIR_SERVER_URL,
        'endpoints': {
            'StructureDefinition': 'StructureDefinition',
            'SearchParameter': 'SearchParameter'
        },
        'username': os.environ.get('SIMPLIFIER_PW'),
        'password': os.environ.get('SIMPLIFIER_USER')
    }
}
