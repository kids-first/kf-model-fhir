import logging
import os

DEFAULT_LOG_LEVEL = logging.DEBUG

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, 'project')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
TORINOX = '~/.dotnet/tools/fhir'
VALIDATE_PROFILE_SH = os.path.join(SCRIPTS_DIR, 'torinox_validate_profile.sh')
VALIDATION_RESULTS_FILES = {'profile': 'profile_validation_results.json',
                            'resource': 'resource_validation_results.json'}

SIMPLIFIER_USER = os.environ.get('SIMPLIFIER_USER')
SIMPLIFIER_PW = os.environ.get('SIMPLIFIER_PW')
SIMPLIFIER_PROJECT_NAME = 'KidsFirstSTU3'
SIMPLIFIER_FHIR_SERVER_URL = f'https://stu3.simplifier.net'

SERVER_HOST = 'localhost'
SERVER_PORT = '8080'
SERVER_BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
CANONICAL_URL = 'http://fhirstu3.kids-first.io/fhir'
PROFILE_ENDPOINT = 'administration/StructureDefinition'
FHIR_XMLNS = 'http://hl7.org/fhir'
