import logging
import os

import pytest
from ncpi_fhir_utility.client import FhirApiClient

from kf_lib_data_ingest.common.io import read_df
from kf_lib_data_ingest.etl.load.load import LoadStage
from kf_model_fhir.ingest_plugin import kids_first_fhir

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCE_DIR = os.path.join("site_root", "input", "resources")
TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
FHIR_API = os.getenv("FHIR_API") or "http://localhost:8000"
FHIR_USER = os.getenv("FHIR_USER") or "admin"
FHIR_PW = os.getenv("FHIR_PW") or "password"


@pytest.fixture(scope="function")
def debug_caplog(caplog):
    """
    pytest capture log output at level=DEBUG
    """
    caplog.set_level(logging.DEBUG)
    return caplog


@pytest.fixture(scope="session")
def client():
    """
    The FhirApiClient instance used for all tests
    """
    return FhirApiClient(base_url=FHIR_API, auth=(FHIR_USER, FHIR_PW))


@pytest.fixture(scope="session")
def load_fhir_resources(client):
    """
    Test session scoped fixture to load test data into server. This is done
    once before any tests run.

    Uses FHIR Ingest Plugin to read in test data from TSV, transform into
    FHIR resources and load into server.

    The FHIR resource types to load are defined in
    kf_model_fhir.ingest_plugin.kids_first_fhir.all_targets
    """
    loader = LoadStage(
        os.path.join(
            ROOT_DIR, "kf_model_fhir", "ingest_plugin", "kids_first_fhir.py"
        ),
        FHIR_API,
        [cls.class_name for cls in kids_first_fhir.all_targets],
        "SD_ME0WME0W",
        cache_dir=os.path.join(TEST_DATA_DIR, "output"),
    )
    loader.run(
        {
            "default": read_df(os.path.join(TEST_DATA_DIR, "default.tsv")),
            "family_relationship": read_df(
                os.path.join(TEST_DATA_DIR, "family_relationships.tsv")
            ),
        }
    )
