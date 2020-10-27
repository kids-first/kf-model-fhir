import os

from kf_lib_data_ingest.common.io import read_df
from kf_lib_data_ingest.common.misc import clean_up_df
from kf_lib_data_ingest.etl.load.load import LoadStage
from kf_model_fhir.ingest_plugin import kids_first_fhir

WORK_DIR = os.path.dirname(__file__)
DATA_DIR = "/Users/kimm11/Documents/workspace/kids-first/kf-ingest-packages/kf_ingest_packages/packages/SD_PREASA7S/initial-ingest/output/GuidedTransformStage"
# DATA_DIR = os.getenv("DATA_DIR")
# STUDY_ID = os.getenv("STUDY_ID")
# USE_ASYNC = os.getenv("USE_ASYNC")

LoadStage(
    os.path.join(WORK_DIR, "kids_first_fhir.py"),
    os.getenv("FHIR_API") or "http://localhost:8000",
    [cls.class_name for cls in kids_first_fhir.all_targets],
    "SD_PREASA7S",
    cache_dir=os.path.join(WORK_DIR, "output"),
    use_async=True,
).run(
    {
        "default": clean_up_df(read_df(f"{DATA_DIR}/default.tsv")),
        "family_relationship": clean_up_df(read_df(f"{DATA_DIR}/family_relationship.tsv"))
    }
)
