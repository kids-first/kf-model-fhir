#!/usr/bin/env python

import sqlalchemy
from urllib.parse import urlparse
import os
from mappings.individual import make_individual

study_id = "SD_PREASA7S"

def db_study_url(db_maintenance_url, study_id):
    return urlparse(db_maintenance_url)._replace(path=f"/{study_id}").geturl()


eng = sqlalchemy.create_engine(
    db_study_url(os.getenv("KF_WAREHOUSE_DB_URL"), study_id),
    connect_args={"connect_timeout": 5},
    server_side_cursors=True
)

schema="Ingest:meen_pcgc/GuidedTransformStage"

result = eng.execute('SELECT * FROM "Ingest:meen_pcgc/GuidedTransformStage".default')
breakpoint()
for r in result:
    print(make_individual(dict(r), study_id))
