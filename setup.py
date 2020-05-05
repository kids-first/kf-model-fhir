import os
from setuptools import setup, find_packages

root_dir = os.path.dirname(os.path.abspath(__file__))
req_file = os.path.join(root_dir, 'requirements.txt')
with open(req_file) as f:
    requirements = f.read().splitlines()

FHIR_VERSION = "4.0.1"
version = __import__('kf_model_fhir').__version__

setup(
    name='kf-model-fhir',
    version=version,
    description=f'Kids First FHIR Model {FHIR_VERSION}',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements
)
