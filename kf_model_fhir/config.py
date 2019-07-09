import logging
import os

from dotenv import load_dotenv

DEFAULT_LOG_LEVEL = logging.DEBUG

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, 'project')
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
VALIDATE_PROFILE_SH = os.path.join(SCRIPTS_DIR, 'torinox_validate_profile.sh')
VALIDATION_RESULTS_FILES = {'profile': 'profile_validation_results.json',
                            'resource': 'resource_validation_results.json'}

load_dotenv(os.path.join(ROOT_DIR, '.env'))
SIMPLIFIER_USER = os.getenv('SIMPLIFIER_USER')
SIMPLIFIER_PW = os.getenv('SIMPLIFIER_PW')
SIMPLIFIER_FHIR_SERVER_URL = 'https://stu3.simplifier.net/KidsFirstSTU3'
CANONICAL_URL = 'http://fhirstu3.kids-first.io/fhir'
SERVER_HOST = 'localhost'
SERVER_PORT = '8080'
SERVER_BASE_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
PROFILE_ENDPOINT = 'administration/StructureDefinition'
TORINOX = '~/.dotnet/tools/fhir'
