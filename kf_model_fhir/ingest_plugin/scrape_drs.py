from concurrent.futures import (
    ThreadPoolExecutor, 
    as_completed,
)

import pandas as pd
import requests

DATA_DIR = "/Users/kimm11/Documents/workspace/kids-first/kf-ingest-packages/kf_ingest_packages/packages/SD_PREASA7S/initial-ingest/output/ExtractStage"
BASE_URL = 'https://kf-api-dataservice.kidsfirstdrc.org'


df = pd.read_csv(f'{DATA_DIR}/genomics.tsv', sep='\t')

external_id_to_latest_did_list = []
for external_id in df['GENOMIC_FILE|ID']:
    resp = requests.get(
        f'{BASE_URL}/genomic-files',
        params={
            'external_id': external_id
        }
    )

    print(resp.status_code)


