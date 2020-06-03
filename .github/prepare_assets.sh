#!/usr/bin/env bash

pip install .
fhirutil validate --publisher_opts="-tx n/a" --clear_output site_root/ig.ini
