import os

from kf_lib_data_ingest.app.settings.development import (  # noqa F401
    SECRETS,
    AUTH_CONFIGS,
)

TARGET_API_CONFIG = os.path.join(
    os.path.dirname(__file__), "kids_first_fhir.py"
)
