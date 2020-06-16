import os
import logging
from collections import defaultdict
from pprint import pprint

import pytest

from kf_lib_data_ingest.etl.load.load import LoadStage
from kf_lib_data_ingest.common.io import read_df
from kf_model_fhir.ingest_plugin import kids_first_fhir
from ncpi_fhir_utility.client import FhirApiClient

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
RESOURCE_DIR = os.path.join('site_root', 'input', 'resources')
TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, 'data')
FHIR_API = os.getenv('FHIR_API') or 'http://localhost:8000'
FHIR_USER = os.getenv('FHIR_USER') or 'admin'
FHIR_PW = os.getenv('FHIR_PW') or 'password'


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
    return FhirApiClient(
        base_url=FHIR_API, auth=(FHIR_USER, FHIR_PW)
    )


@pytest.fixture(scope="session")
def prepare_data():
    """
    Use fixed target service ids to ensure PUT is used to submit resources
    This makes tests idempotent when run repeatedly (on local machine)
    """
    df = read_df(os.path.join(TEST_DATA_DIR, 'study_df.tsv'))
    ids = defaultdict(set)
    for idx, row in df.reset_index().iterrows():
        for cls in kids_first_fhir.all_targets:
            _id = f'{cls.class_name}-{idx}'
            df.at[idx, cls.target_id_concept] = _id
            ids[cls.api_path].add(_id)
    return df, ids


@pytest.fixture(scope="session")
def load_fhir_resources(prepare_data, client):
    """
    Test session scoped fixture to load test data into server. This is done
    once before any tests run.

    Uses FHIR Ingest Plugin to read in test data from TSV, transform into
    FHIR resources and load into server.

    The FHIR resource types to load are defined in
    kf_model_fhir.ingest_plugin.kids_first_fhir.all_targets
    """
    df, ids = prepare_data

    loader = LoadStage(
        os.path.join(
            ROOT_DIR, 'kf_model_fhir', 'ingest_plugin', 'kids_first_fhir.py'
        ),
        FHIR_API,
        [
            cls.class_name
            for cls in kids_first_fhir.all_targets
        ],
        'SD_ME0WME0W',
        cache_dir=os.path.join(TEST_DATA_DIR, 'output')
    )
    loader.run({'default': df})


def clean(client, ids):
    """
    Delete submitted data in server - use when desired
    """
    for api_path, instance_ids in ids.items():
        for _id in instance_ids:
            success, result = client.send_request(
                'delete', f'{client.base_url}{api_path}/{_id}'
            )
