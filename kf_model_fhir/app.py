import logging

from requests.auth import HTTPBasicAuth

from kf_model_fhir.config import (
    SIMPLIFIER_PROJECT_NAME,
    SIMPLIFIER_FHIR_SERVER_URL,
)
from kf_model_fhir.validation import FhirValidator
from kf_model_fhir import loader

logger = logging.getLogger(__name__)


def publish_to_simplifier(resource_dir, resource_type='profile',
                          username=None, password=None,
                          project_name=None):
    """
    Publish resource files in resource_dir to Simplifier.net project

    Profiles are published by running validation since validation creates
    profiles on the server

    :param resource_dir: directory containing FHIR resource files
    :type resource_dir: str
    :param resource_type: directory containing FHIR resource files
    :type resource_type: str
    :param username: Simplifier account username
    :type username: str
    :param password: Simplifier account password
    :type password: str
    :param project_name: Simplifier project_name
    :type project_name: str

    :returns: a boolean indicating if publish was successful
    """
    project_name = project_name or SIMPLIFIER_PROJECT_NAME
    project_name = ''.join(project_name.split(' '))
    base_url = f'{SIMPLIFIER_FHIR_SERVER_URL}/{project_name}'

    if username and password:
        auth = HTTPBasicAuth(username, password)

    logger.info(
        f'Begin publishing {resource_type} in {resource_dir} '
        f'to Simplifier project {base_url}'
    )

    # Publish profiles to simplifier
    success = True
    fhir_validator = FhirValidator(base_url=base_url, auth=auth)
    if resource_type == 'profile':
        fhir_validator.endpoints['profile'] = (
            f"{base_url}/StructureDefinition"
        )
        success = fhir_validator.validate('profile', resource_dir)

    # Publish resources to simplifier
    else:
        # Delete all existing resources
        resources = loader.load_resources(resource_dir)
        for rd in resources:
            rd['endpoint'] = f'{base_url}/{rd["resource_type"]}'
            success_delete = fhir_validator.client.delete_all(rd['endpoint'])
            if not success_delete:
                logger.warning(
                    f'⚠️ Failed to delete all resources at {rd["endpoint"]}'
                )
            success = success_delete & success

        # Create new resources
        success_create_all, _ = fhir_validator.client.post_all(resources)

    return success_create_all & success
