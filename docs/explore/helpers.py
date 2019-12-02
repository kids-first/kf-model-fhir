import os
from copy import deepcopy
from pprint import pprint, pformat

from click.testing import CliRunner
from requests.auth import HTTPBasicAuth

from kf_model_fhir import cli
from kf_model_fhir.client import FhirApiClient
from kf_model_fhir.loader import load_resources
from kf_model_fhir.config import PROJECT_DIR, SERVER_CONFIG, FHIR_VERSION

# Remove the local vonk server for now
# We have a public vonk server to use instead
SERVER_CONFIG.pop('vonk', None)
runner = CliRunner()
client = FhirApiClient(fhir_version=FHIR_VERSION)


def run_cli_cmd(cmd_name, params_list):
    """
    Run a fhirmodel CLI command
    """
    cmd = getattr(cli, cmd_name)
    result = runner.invoke(cmd, params_list)
    if result.exit_code != 0:
        print(result.output)
        raise Exception(result.exception)


def emoji(resp):
    """
    Return an emoji based on the `total` value in a FHIR GET response
    """
    total = resp.get('total', None)
    if total is None:
        return '❌'
    if total > 0:
        return '✅'
    else:
        return '⚠️ or ✅'


def load_fhir_token_search_params(username, password):
    """
    Just for Aidbox - load token type Aidbox SearchParameters
    """
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
        client.send_request(
            'put', url, auth=HTTPBasicAuth(username, password), json=aidbox_sp
        )


def load_aidbox_extensions(username, password):
    """
    Just for Aidbox - load Aidbox Attributes (Extensions)
    """
    base_url = SERVER_CONFIG['aidbox']['base_url']

    # Load Aidbox Extensions
    print('Loading Aidbox Extensions ...')

    # Just Patient cohort id for now
    ext = {
        "resourceType": "Patient",
        "path": ["cohort_id"],
        "id": "Patient.cohort_id",
        "type": "string",
        "description": "The identifier of the cohort to which patient belongs"
    }
    url = f'{base_url.rstrip("/fhir")}/Attribute/{ext["id"]}'
    client.send_request(
        'put', url, auth=HTTPBasicAuth(username, password), json=ext
    )


def execute_queries(queries, expected_counts={}, display_content=False):
    """
    Run all queries in `queries` on every server
    Display results
    """
    for query in queries:
        dlen = len(query['desc'])
        print('*' * dlen)
        print(query['desc'])
        print('*' * dlen)
        for server_name, settings in SERVER_CONFIG.items():
            print(server_name.upper())
            print('-' * len(server_name))
            url = f"{settings['base_url']}/{query['endpoint']}"
            uname = settings.get('username')
            pw = settings.get('password')
            params = query['params']
            params.update({'_total': 'accurate'})
            auth = HTTPBasicAuth(uname, pw)
            success, resp = client.send_request(
                'get', url, auth=auth, params=params
            )

            if display_content:
                pprint(resp)

            print(f"{emoji(resp)} Found {resp.get('total')} "
                  f"{query['endpoint'].lstrip('/')} "
                  f"matching these params {pformat(params)}")
            if resp.get('total') == expected_counts.get(query['endpoint']):
                print(
                    f'⚠️ ？ The returned total = actual count of '
                    f'{query["endpoint"]}. This may or may not be correct. '
                    'Some servers ignore search parameters that they do not '
                    'understand, which results in a get all query. '
                )
            print('\n')


def load_all_servers(server_names=None):
    """
    Publish profiles and resources to all servers listed in server_names
    or SERVER_CONFIG
    """
    server_names = server_names or SERVER_CONFIG.keys()
    for server_name in server_names:
        # Profiles
        server_settings = SERVER_CONFIG.get(server_name)
        if not server_settings:
            print(f'⚠️ No such server exists: {server_name}')
            continue

        print(f'\n\n********************** {server_name.upper()} **********************')
        username = server_settings.get('username')
        password = server_settings.get('password')
        params = [os.path.join(PROJECT_DIR, 'profiles'), '--resource_type', 'profile',
                  '--server_name', server_name]
        if username and password:
            params.extend(['--username', username, '--password', password])

        if server_name == 'aidbox':
            params.extend(['-e', 'search_parameter'])
            load_fhir_token_search_params(username, password)
            # load_aidbox_extensions(username, password)

        run_cli_cmd('publish', params)

        # Resources
        params = [os.path.join(PROJECT_DIR, 'resources'), '--resource_type', 'resource',
                  '--server_name', server_name]
        if username and password:
            params.extend(['--username', username, '--password', password])

        run_cli_cmd('publish', params)
        print(f'\n\n*******************************************************************')
