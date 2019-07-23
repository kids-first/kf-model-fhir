"""
Class that is responsible validating FHIR profiles and resources
"""

import os
import logging
from collections import defaultdict
from pprint import pformat

from kf_model_fhir import __fhir_version__ as FHIR_VERSION
from kf_model_fhir.config import (
    PROJECT_DIR,
    CANONICAL_URL,
    SERVER_BASE_URL,
    PROFILE_ENDPOINT,
    VALIDATION_RESULTS_FILES
)
from kf_model_fhir.utils import write_json
from kf_model_fhir.client import FhirApiClient
from kf_model_fhir import loader

SUCCESS_KEY = 'success'
ERROR_KEY = 'errors'


class FhirValidator(object):

    def __init__(self, base_url=SERVER_BASE_URL, auth=None):
        self.logger = logging.getLogger(type(self).__name__)
        self.client = FhirApiClient(base_url=base_url, auth=auth)
        self.client.check_service_status(
            exit_on_down=True,
            log_msg=f'FHIR validation server {self.client.base_url} must be '
            'up in order to continue with validation'
        )
        self.profiles = []
        self.extensions = []
        self.resources = []
        self.endpoints = {
            'profile': f'{base_url}/{PROFILE_ENDPOINT}'
        }

    def validate(self, resource_type, data_path):
        """
        Validate FHIR Profiles or example FHIR Resources against the profiles.

        If extension type profiles exist then they will be validated before
        other profiles are validated. Extensions should be placed in a
        subdirectory of data_path, called `extensions`.

        :param data_path: directory or file path to the resource file(s)
        :type data_path: str

        :returns: boolean indicating successful validation
        """
        if not data_path:
            data_path = os.path.join(PROJECT_DIR, resource_type + 's')

        self.logger.info(
            f'Starting FHIR {FHIR_VERSION} {resource_type} validation for '
            f'{data_path}'
        )

        if resource_type == 'profile':
            success, results = self.validate_profiles(data_path)
        else:
            success, results = self.validate_resources(data_path)

        if not success:
            self.logger.error(f'❌ {resource_type.title()} validation failed!')
        else:
            self.logger.info(f'✅ {resource_type.title()} validation passed!')

        # Write validation results
        self.write_validation_results(results, resource_type)

        return success

    def validate_profiles(self, data_path):
        """
        Validate FHIR profiles by creating them on the FHIR server

        Delete existing profiles on FHIR server first
        Look for any extension type profiles in a subdirectory of data_path
        called `extensions`. If extensions exist, validate them first,
        before other profiles.

        :param data_path: directory or file path to the resource file(s)
        :type data_path: str

        :returns: a tuple (success boolean, validation results dict)
        """
        success = True
        results = defaultdict(dict)
        data_path = os.path.abspath(os.path.expanduser(data_path))

        # Delete all profiles
        success = self.client.delete_all(self.endpoints['profile'],
                                         params={'url:below': CANONICAL_URL})
        if not success:
            self.logger.error('Failed to delete existing profiles. Exiting')
            exit(1)

        if not self.profiles:
            self.profiles = loader.load_resources(data_path)

        # Validate profiles
        success, results = self.validate_structure_defs(self.profiles)

        return success, results

    def validate_structure_defs(self, resource_dicts):
        """
        Validate FHIR StructureDefinition(s) by POSTing new profiles
        on FHIR server

        :param resource_dicts: list of dicts containing resources loaded from
        files
        :type resource_dicts: list of dicts

        :returns: a tuple (success boolean, validation results dict)
        """
        success = True
        results = {}
        if len(resource_dicts) == 0:
            self.logger.info('0 resources loaded. Nothing to validate')
            return success, results

        # Create on server to validate
        success, results = self.client.post_all(
            resource_dicts,
            endpoint=self.endpoints['profile']
        )

        return success, results

    def validate_resources(self, data_path):
        """
        Validate FHIR Resources against profiles

        Check each resource has a referenced profile in its meta.profile
        element.
        Validate by POSTing to /<resource name>/$validate

        :param data_path: directory or file path to the resource file(s)
        :type data_path: str

        :returns: a tuple (success boolean, validation results dict)
        """
        success = True
        results = {}

        # Gather resource payloads to validate
        if not self.resources:
            self.resources = loader.load_resources(data_path)

        if len(self.resources) == 0:
            self.logger.info('0 resources loaded. Nothing to validate')
            return success, results

        # Check that each resource has a referenced profile
        reference_errors = {}
        for resource_dict in self.resources:
            filename = resource_dict['filename']
            filepath = resource_dict['filepath']
            resource = resource_dict['content']
            profile = resource.get('meta', {}).get('profile')
            success_ref_profile = True

            if profile is None:
                rt = resource_dict['resource_type']
                profile_uri = f'{CANONICAL_URL}/StructureDefinition/{rt}'
                display = {'meta': {'profile': profile_uri}}
                err_msg = (
                    f"Profile canonical url missing in {filename}. "
                    "When validating a resource, you must specify which "
                    "profile to use via its canonical URL. You can do this by "
                    "adding the 'meta' object to your resource payload. "
                    f"A JSON example looks like: {pformat(display)} "
                )
                self.logger.info(err_msg)
                reference_errors[filepath] = err_msg
                success = success_ref_profile & success

            rt = resource_dict["resource_type"]
            resource_dict['endpoint'] = (
                f'{self.client.base_url}/{rt}/$validate'
            )

        if success:
            # Send to server for further validation
            success, results = self.client.post_all(self.resources)
        else:
            results[ERROR_KEY] = reference_errors

        return success, results

    def write_validation_results(self, results, resource_type):
        """
        Collect successes, errors, and write validate results
        to appropriate file for resource_type

        :param result_dicts: list of validation result dicts
        :type result_dicts: list of dicts
        :param resource_type: one of [profile | resource]
        :type resource_type: str
        """
        if results:
            results_filepath = os.path.join(
                os.getcwd(), VALIDATION_RESULTS_FILES.get(resource_type)
            )
            if os.path.isfile(results_filepath):
                os.remove(results_filepath)
            write_json(results, results_filepath)

            self.logger.info(f'See validation results in {results_filepath}')
