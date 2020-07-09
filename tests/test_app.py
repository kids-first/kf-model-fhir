import os
from pprint import pprint

from ncpi_fhir_utility import cli
from ncpi_fhir_utility.loader import load_resources

import pytest
from click.testing import CliRunner
from conftest import RESOURCE_DIR, FHIR_API, FHIR_USER, FHIR_PW

SEARCH_PARAM_DIR = os.path.join(RESOURCE_DIR, "search")
ASIAN = "2028-9"
NON_HISPANIC = "2186-5"


@pytest.mark.parametrize(
    "resource_dir",
    [
        (os.path.join(RESOURCE_DIR, "terminology")),
        (os.path.join(RESOURCE_DIR, "extensions")),
        (os.path.join(RESOURCE_DIR, "profiles")),
        (os.path.join(RESOURCE_DIR, "search")),
        # TODO - This fails because we don't have the external terminology
        # server setup with our integration test server.
        # Once that is complete, then uncomment the line below
        # (os.path.join(RESOURCE_DIR, 'examples'),
    ],
)
def test_deploy_model(resource_dir):
    """
    Test loading the FHIR model into the integration test server

    Order of load: terminology, extensions, profiles, search parameters,
    example resources.
    """
    runner = CliRunner()
    result = runner.invoke(
        cli.publish,
        [
            resource_dir,
            "--base_url",
            FHIR_API,
            "--username",
            FHIR_USER,
            "--password",
            FHIR_PW,
        ],
    )
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "resource_type, expected_count",
    [
        ("Practitioner", 1),
        ("Organization", 1),
        ("PractitionerRole", 1),
        ("Patient", 10),
        ("Group", 3),
        ("ResearchStudy", 1),
        ("Condition", 10),
        ("Observation", 10),
        ("Specimen", 10),
        # Add additional tuples of the form: (resource_type, expected_count)
    ],
)
def test_ingest_plugin(
    client, load_fhir_resources, resource_type, expected_count
):
    """
    Test Kids First FHIR ingest plugin

    Uses the load_fhir_resources test fixture to read data in from
    tests/data/study_df.tsv, transform into FHIR resources, and load into the
    test FHIR server.

    Tests check that the number of instances of a resource type match the
    expected count for that resource type.

    :param client: See conftest.client
    :param load_fhir_resources: See conftest.load_fhir_resources
    :param resource_type: FHIR resource type being tested
    :param expected_count: Expected count of resource_type in server
    """
    success, result = client.send_request(
        "get",
        f"{client.base_url}/{resource_type}",
        params={"_total": "accurate"},
    )
    assert success
    assert result["response"]["total"] == expected_count


@pytest.mark.parametrize(
    "search_param_filename, resource_type, search_value, expected_count",
    [
        ("SearchParameter-us-core-race.json", "Patient", ASIAN, 4),
        ("SearchParameter-us-core-ethnicity.json", "Patient", NON_HISPANIC, 10),
    ],
)
def test_search_params(
    client, search_param_filename, resource_type, search_value, expected_count
):
    """
    Test SearchParameters

    Query the test server at the /{resource_type} endpoint using the
    search parameter and specified search value. Check that the returned total
    matches specified expected count.
    """
    sp = load_resources(os.path.join(SEARCH_PARAM_DIR, search_param_filename))[
        0
    ]["content"]
    success, result = client.send_request(
        "get",
        f"{client.base_url}/{resource_type}",
        params={sp["code"]: search_value, "_total": "accurate"},
    )
    assert success
    pprint(result)
    assert result["response"]["total"] == expected_count
