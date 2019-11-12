"""
Class that is responsible validating FHIR profiles and resources
"""

import os
import logging
from collections import defaultdict
from pprint import pformat

from requests.auth import HTTPBasicAuth

from kf_model_fhir.config import (
    FHIR_VERSION,
    PROJECT_DIR,
    CANONICAL_URL,
    SERVER_CONFIG,
    VALIDATION_RESULTS_FILES
)
from kf_model_fhir.utils import write_json
from kf_model_fhir.client import FhirApiClient
from kf_model_fhir import loader

SUCCESS_KEY = 'success'
ERROR_KEY = 'errors'


class FhirValidator(object):

    def __init__(self, server_cfg=None, username=None, password=None):
        self.logger = logging.getLogger(type(self).__name__)

        if username and password:
            auth = HTTPBasicAuth(username, password)
        else:
            auth = None
        server_cfg = server_cfg or SERVER_CONFIG.get('vonk')
        base_url = server_cfg.get('base_url')

        self.client = FhirApiClient(
            base_url=base_url,
            status_endpoint=server_cfg.get('status_url', base_url),
            auth=auth,
            fhir_version=FHIR_VERSION
        )
        self.client.check_service_status(
            exit_on_down=True,
            log_msg=f'FHIR validation server {self.client.base_url} must be '
            'up in order to continue with validation'
        )
        self.profiles = []
        self.extensions = []
        self.resources = []
        self.search_parameters = []
        self.endpoints = {
            'profile': f"{base_url}/{server_cfg['endpoints']['profile']}",
            'search_parameter':
                f"{base_url}/{server_cfg['endpoints']['search_parameter']}"
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

        # Delete all StructureDefinitions
        success = self.client.delete_all(self.endpoints['profile'],
                                         params={'url:below': CANONICAL_URL})

        # Validate extensions
        success, results = self.validate_extensions(data_path)
        if not success:
            self.write_validation_results(results, 'profile')
            return success, results

        # Validate referenced extensions
        if not self.profiles:
            self.profiles = loader.load_resources(data_path)
        success, results = self.validate_referenced_extensions(
            self.profiles
        )
        if not success:
            self.write_validation_results(results, 'profile')
            return success, results

        # Delete all SearchParameter
        success = success & self.client.delete_all(
            self.endpoints['search_parameter'],
            params={'url:below': CANONICAL_URL}
        )
        if not success:
            self.logger.error('Failed to delete existing profiles. Exiting')
            exit(1)

        # Validate search parameters
        success, results = self.validate_search_params(data_path)
        if not success:
            self.write_validation_results(results, 'profile')
            return success, results

        # Validate profiles
        success, results = self.validate_conformance_res(self.profiles)

        return success, results

    def validate_search_params(self, profiles_path):
        """
        Validate search_parameters if they exist
        Look for any search_parameter profiles in a subdirectory of
        profiles_path called `search_parameters`.

        :returns: a tuple (success boolean, validation results dict)
        """
        success = True
        results = defaultdict(dict)

        self.logger.info('Begin search_parameter profile validation ...')

        if os.path.isdir(profiles_path):
            d = os.path.join(profiles_path, 'search_parameters')
        else:
            d = (
                os.path.join(os.path.dirname(profiles_path),
                             'search_parameters')
            )
        if not os.path.exists(d):
            self.logger.info(
                f'Search parameter dir {d} not found. '
                'Nothing to validate'
            )
            return success, results

        if len(os.listdir(d)) == 0:
            self.logger.info(
                f'0 search parameters found in {d}. Nothing to validate'
            )
            return success, results

        if not self.search_parameters:
            self.search_parameters = loader.load_resources(d)
        success, results = self.validate_conformance_res(
            self.search_parameters, resource_type='search_parameter'
        )

        if success:
            self.logger.info('✅ SearchParameter validation passed!')
        else:
            self.logger.info("❌ SearchParameter validation failed!")

        return success, results

    def validate_extensions(self, profiles_path):
        """
        Validate extensions if they exist
        Look for any extension type profiles in a subdirectory of profiles_path
        called `extensions`.

        :returns: a tuple (success boolean, validation results dict)
        """
        success = True
        results = defaultdict(dict)

        self.logger.info('Begin extension profile validation ...')

        if os.path.isdir(profiles_path):
            extension_dir = os.path.join(profiles_path, 'extensions')
        else:
            extension_dir = (
                os.path.join(os.path.dirname(profiles_path), 'extensions')
            )
        if not os.path.exists(extension_dir):
            self.logger.info(
                f'Extension dir {extension_dir} not found. '
                'Nothing to validate'
            )
            return success, results

        if len(os.listdir(extension_dir)) == 0:
            self.logger.info(
                f'0 extensions found in {extension_dir}. Nothing to validate'
            )
            return success, results

        if not self.extensions:
            self.extensions = loader.load_resources(extension_dir)
        success, results = self.validate_conformance_res(self.extensions)

        if success:
            self.logger.info('✅ Extension validation passed!')
        else:
            self.logger.info("❌ Extension validation failed!")

        return success, results

    def validate_referenced_extensions(self, profile_dicts):
        """
        Validate extensions referenced in profiles by ensuring they exist
        on the FHIR server.

        Write errors to results dict keyed by profile filepath

        :param profile_dicts: list of profiles to validate.
        :type profile_dicts: list of profile dicts
        See loader.read_resource_file for details on format of dicts

        :return: results dict
        """
        success = True
        results = defaultdict(dict)

        self.logger.info('Begin reference extension validation ...')
        for pd in profile_dicts:
            self.logger.info(
                f'Validating reference extensions in {pd["filename"]}'
            )
            content = pd['content']
            elems = content.get('differential', {}).get('element', [])
            extensions = [el for el in elems if 'extension' in el.get('id')]
            errors = []
            for extension in extensions:
                result = defaultdict(dict)
                self._check_referenced_exts_exist(extension, result)

                if not (len(result.get(ERROR_KEY, {}).keys()) == 0):
                    errors.append(result[ERROR_KEY])

            if errors:
                success = False
                results[ERROR_KEY][pd['filepath']] = errors

        return success, results

    def _check_referenced_exts_exist(self, input_, result):
        """
        Find any profile references in input_, an extension dict, and check
        that they exist on the validation server

        The result dict looks like:
            {
                SUCCESS_KEY: {
                    '/StructureDefinition/probandStatus': <result dict>,
                    ...
                },
                ERROR_KEY: {
                    '/StructureDefinition/birthPlace': <result dict>,
                    ...
                }
            }

        :param input_: extension element in a profile's extensions list
        :type input_: dict
        :returns: result dict
        """
        profile_endpoint = self.endpoints['profile']

        if isinstance(input_, dict):
            for k, v in input_.items():
                if k == 'profile':
                    if isinstance(v, str):
                        vals = [v]
                    else:
                        vals = v
                    for v in vals:
                        self.logger.debug(f'Checking if {v} exists on server')
                        success, result_1 = self.client.send_request(
                            'get',
                            profile_endpoint,
                            auth=self.client.auth,
                            params={
                                'url': v,
                                '_total': 'accurate'
                            })
                        success = success and result_1['response']['total'] > 0
                        profile_relative_url = v.split(CANONICAL_URL)[-1]
                        if success:
                            self.logger.info(
                                f'✅ Referenced extension found: {v}'
                            )
                            result[SUCCESS_KEY][profile_relative_url] = (
                                result_1
                            )
                        else:
                            msg = f'❌ Referenced extension not found: {v}'
                            self.logger.info(msg)
                            result_1['message'] = msg
                            result[ERROR_KEY][profile_relative_url] = result_1
                else:
                    self._check_referenced_exts_exist(v, result)

        elif isinstance(input_, list):
            for val in input_:
                self._check_referenced_exts_exist(val, result)

    def validate_conformance_res(self, resource_dicts,
                                 resource_type='profile'):
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

        # Check that fhir version in resource file matches app's
        # config.FHIR_VERSION
        for rd in resource_dicts:
            if 'fhirVersion' not in rd['content']:
                continue
            version = rd['content'].get('fhirVersion')
            if version != FHIR_VERSION:
                raise Exception(
                    f'Fhir version conflict! Detected version: "{version}" in '
                    f'{rd["filepath"]}, and version "{FHIR_VERSION}" in app '
                    'config.py. Fhir version in StructureDefinition resources '
                    'must all be the same and match the version in the app '
                    'config.py'
                )

        # Create on server to validate
        success, results = self.client.post_or_put_all(
            resource_dicts,
            endpoint=self.endpoints[resource_type]
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
            resource = resource_dict['content']
            profile = resource.get('meta', {}).get('profile')

            if profile is None:
                rt = resource_dict['resource_type']
                profile_uri = f'{CANONICAL_URL}/StructureDefinition/{rt}'
                display = {'meta': {'profile': [profile_uri]}}
                err_msg = (
                    f"Profile canonical url missing in {filename}. "
                    "When validating a resource, you should specify which "
                    "profile to use via its canonical URL. You can do this by "
                    "adding the 'meta' object to your resource payload. "
                    f"A JSON example looks like: {pformat(display)} "
                )
                self.logger.warning(err_msg)

            rt = resource_dict["resource_type"]
            resource_dict['endpoint'] = (
                f'{self.client.base_url}/{rt}/$validate'
            )

        # Send valid resources to server for further validation
        success, results = self.client.post_or_put_all(
            [r for r in self.resources
             if r['filepath'] not in reference_errors]
        )

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
