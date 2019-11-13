import os
import json
from copy import deepcopy
from pprint import pformat

import requests

from requests.auth import HTTPBasicAuth

from kf_model_fhir.loader import load_resources
from kf_model_fhir.config import PROJECT_DIR, SERVER_CONFIG


def send_request(method_name, url, username=None, password=None,
                 **request_kwargs):
    http_method = getattr(requests, method_name.lower())

    if username and password:
        request_kwargs['auth'] = HTTPBasicAuth(username, password)

    ct = {
        'Content-Type': 'application/fhir+json; fhirVersion=4.0'
    }
    headers = request_kwargs.get('headers', {})
    headers.update(ct)
    request_kwargs['headers'] = headers

    r = http_method(url, **request_kwargs)

    try:
        resp_content = r.json()
    except json.decoder.JSONDecodeError:
        resp_content = r.text
    if r.status_code > 300:
        print(
            f'Error with request. Status: {r.status_code}. '
            f'Caused by: {pformat(resp_content)}'
        )

    print(f'Success: {method_name.upper()} {url}')

    return resp_content, r.status_code


def get(url, username=None, password=None, **request_kwargs):
    return send_request(
        'get', url, username=username, password=password, **request_kwargs
    )


def load_search_params(username, password):
    base_url = SERVER_CONFIG['aidbox']['base_url']

    # Load Aidbox Search Parameters
    print('Loading Aidbox SearchParameters ...')
    search_param_template = {
        "name": "",
        "type": "token",
        "resource": {"id": "Patient", "resourceType": "Entity"},
        "expression": []
    }
    search_params = load_resources(
        os.path.join(PROJECT_DIR, 'profiles', 'search_parameters')
    )
    url = f'{base_url.rstrip("/fhir")}/SearchParameter'
    for s in search_params:
        exp = s['content']['expression']
        filter_ = exp.split('=')[-1].split(')')[0].strip()
        name = s['content']['code']
        base = s['content']['base'][0]
        aidbox_sp = deepcopy(search_param_template)
        aidbox_sp['id'] = f'{base}.{name}'
        aidbox_sp['name'] = name
        aidbox_sp['resource']['id'] = base
        aidbox_sp['expression'] = [
            [
                "extension",
                {"url": filter_.strip("'")},
                "valueCoding",
                "code"
            ]
        ]
        url = f"{url}/{aidbox_sp['id']}"
        send_request(
            'put', url, username=username, password=password, json=aidbox_sp
        )
