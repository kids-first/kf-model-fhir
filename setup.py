import os
from setuptools import setup, find_packages

from kf_model_fhir.config import FHIR_VERSION

root_dir = os.path.dirname(os.path.abspath(__file__))
req_file = os.path.join(root_dir, 'requirements.txt')
with open(req_file) as f:
    requirements = f.read().splitlines()

version = __import__('kf_model_fhir').__version__

setup(
    name='kf-model-fhir',
    version=version,
    description=f'Kids First FHIR Model {FHIR_VERSION}',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fhirmodel=kf_model_fhir.cli:cli',
        ],
    },
    include_package_data=True,
    install_requires=requirements
)
