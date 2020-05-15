"""
Quickstart

1. Pip-install the following dependencies:

- sqlalchemy
- psycopg2
- -e git+https://github.com/kids-first/kf-lib-data-ingest#egg=kf-lib-data-ingest

2. Export the following environmental variables: 

- KF_WAREHOUSE_DB_URL=
- FHIR_USER=
- FHIR_PASS=

3. Tunnel to Bastion dev and run.

For the detailed explanaion of arguments, please execute python loader.py -h.
"""
import os
import argparse
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pformat, pprint

import sqlalchemy as sa

from ncpi_fhir_utility.client import FhirApiClient

from resources.practitioner import yield_practitioners
from resources.organization import yield_organizations
from resources.practitioner_role import yield_practitioner_roles
from resources.kfdrc_research_study import yield_kfdrc_research_studies
from resources.kfdrc_patient import yield_kfdrc_patients
from resources.kfdrc_condition import yield_kfdrc_conditions
from resources.kfdrc_phenotype import yield_kfdrc_phenotypes
from resources.kfdrc_vital_status import yield_kfdrc_vital_statuses
from resources.kfdrc_specimen import yield_kfdrc_specimens


def db_study_url(db_maintenance_url, study_id):
    return urlparse(db_maintenance_url)._replace(path=f'/{study_id}').geturl()


def send_resource(payload):
    endpoint = f'{client.base_url}/{payload["resourceType"]}/{payload["id"]}'
    success, result = client.send_request('PUT', endpoint, json=payload)
    return success, result, payload


def consume_futures(futures):
    for future in as_completed(futures):
        success, result, payload = future.result()
        print(f'Sent {payload["id"]}')
        if not success:
            raise Exception(
                f'''
                Failed to submit:\n{pformat(payload)}\n{'-'*80}\n{pformat(result)}
                '''
            )


# Read in evironmental variables
KF_WAREHOUSE_DB_URL = os.getenv('KF_WAREHOUSE_DB_URL')
FHIR_USER = os.getenv('FHIR_USER')
FHIR_PASS = os.getenv('FHIR_PASS')

# Read in CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument('study_id', help='Kids First study ID (e.g. SD_PREASA7S)')
parser.add_argument(
    '-t', '--target_url',
    default='http://localhost:8000',
    help='a target service URL where data will be loaded into'
)
parser.add_argument(
    '-i', '--ingest_package',
    default='initial-ingest',
    help='an ingest package name that data will be pulled from'
)

# Parse arguments
args = parser.parse_args()
study_id = args.study_id
target_url = args.target_url
ingest_package = args.ingest_package

# Create DB engine connection
engine = sa.create_engine(
    db_study_url(KF_WAREHOUSE_DB_URL, study_id),
    connect_args={'connect_timeout': 5},
    server_side_cursors=True
)
schema=f'Ingest:{ingest_package}:GuidedTransformStage'
table = f'"{schema}".default'

# Instantiate FHIR API client
client = FhirApiClient(base_url=target_url, auth=(FHIR_USER, FHIR_PASS))

# Load resources
with ThreadPoolExecutor(max_workers=10) as tpex:
    # Practitioners
    practitioners = {}
    futures = []
    for payload, name in yield_practitioners(engine, table):
        futures.append(tpex.submit(send_resource, payload))
        practitioners[name] = payload
    consume_futures(futures)

    # Organizations
    organizations = {}
    futures = []
    for payload, institution in yield_organizations(engine, table):
        futures.append(tpex.submit(send_resource, payload))
        organizations[institution] = payload
    consume_futures(futures)

    # PractitionerRoles
    practitioner_roles = {}
    for payload, (institution, name) in yield_practitioner_roles(
            engine, table, practitioners, organizations
        ):
        futures.append(tpex.submit(send_resource, payload))
        practitioner_roles[(institution, name)] = payload
    consume_futures(futures)

    # KF DRC ResearchStudies
    for payload in yield_kfdrc_research_studies(
            engine, table, study_id, organizations, practitioner_roles
        ):
        futures.append(tpex.submit(send_resource, payload))
    consume_futures(futures)

    # KF DRC Patients
    kfdrc_patients = {}
    futures = []
    for payload, kfdrc_patient_id in yield_kfdrc_patients(engine, table, study_id):
        futures.append(tpex.submit(send_resource, payload))
        kfdrc_patients[kfdrc_patient_id] = payload
    consume_futures(futures)

    # KF DRC Conditions
    futures = []
    for payload in yield_kfdrc_conditions(engine, table, study_id, kfdrc_patients):
        futures.append(tpex.submit(send_resource, payload))
    consume_futures(futures)

    # KF DRC phenotypes
    futures = []
    for payload in yield_kfdrc_phenotypes(engine, table, study_id, kfdrc_patients):
        futures.append(tpex.submit(send_resource, payload))
    consume_futures(futures)

    # KF DRC Vital Statuses
    futures = []
    for payload in yield_kfdrc_vital_statuses(engine, table, study_id, kfdrc_patients):
        futures.append(tpex.submit(send_resource, payload))
    consume_futures(futures)

    # KF DRC Specimens
    kfdrc_specimens = {}
    futures = []
    for payload, kfdrc_specimen_id in yield_kfdrc_specimens(engine, table, study_id, kfdrc_patients):
        futures.append(tpex.submit(send_resource, payload))
        kfdrc_specimens[kfdrc_specimen_id] = payload
    consume_futures(futures)
