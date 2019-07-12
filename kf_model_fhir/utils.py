from copy import deepcopy
import datetime
import json
import logging
import os
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from kf_model_fhir.config import DEFAULT_LOG_LEVEL

logger = logging.getLogger(__name__)


def setup_logger(log_level=DEFAULT_LOG_LEVEL):
    """
    Configure and create the logger

    :param log_level: a string specifying what level of log messages to record
    in the log file. Values are not case sensitive. The list of acceptable
    values are the names of Python's standard lib logging levels.
    (critical, error, warning, info, debug, notset)
    """
    DEFAULT_FORMAT = (
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Setup console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(DEFAULT_FORMAT))

    # Set log level and handlers
    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(consoleHandler)


def timestamp():
    """
    Helper to create an ISO 8601 formatted string that represents local time
    and includes the timezone info.
    """
    # Calculate the offset taking into account daylight saving time
    # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    if time.localtime().tm_isdst:
        utc_offset_sec = time.altzone
    else:
        utc_offset_sec = time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    t = datetime.datetime.now().replace(
        tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    return str(t)


def read_json(filepath, default=None):
    """
    Read JSON file into Python dict. If default is not None and the file
    does not exist, then return default.

    :param filepath: path to JSON file
    :type filepath: str
    :param default: default return value if file not found, defaults to None
    :type default: any, optional
    :return: your data
    :rtype: dict
    """
    if (default is not None) and (not os.path.isfile(filepath)):
        return default

    with open(filepath, 'r') as data_file:
        return json.load(data_file)


def write_json(data, filepath, **kwargs):
    r"""
    Write Python dict to JSON file.

    :param data: your data
    :type data: dict
    :param filepath: where to write your JSON file
    :type filepath: str
    :param \**kwargs: keyword arguments to pass to json.dump
    """
    if 'indent' not in kwargs:
        kwargs['indent'] = 4
    if 'sort_keys' not in kwargs:
        kwargs['sort_keys'] = True
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, **kwargs)


def requests_retry_session(
        session=None, total=10, read=10, connect=1, status=10,
        backoff_factor=5, status_forcelist=(500, 502, 503, 504)
):
    """
    Send an http request and retry on failures or redirects

    See urllib3.Retry docs for details on all kwargs except `session`
    Modified source: https://www.peterbe.com/plog/best-practice-with-retries-with-requests # noqa E501

    :param session: the requests.Session to use
    :param total: total retry attempts
    :param read: total retries on read errors
    :param connect: total retries on connection errors
    :param status: total retries on bad status codes defined in
    `status_forcelist`
    :param backoff_factor: affects sleep time between retries
    :param status_forcelist: list of HTTP status codes that force retry
    """
    session = session or requests.Session()

    retry = Retry(
        total=total,
        read=read,
        connect=connect,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def check_service_status(url, exit_on_down=False, **request_kwargs):
    """
    Check service status and optionally exit program if server returns
    non-200 status code
    """
    # Check service
    try:
        response = requests_retry_session(total=1,
                                          connect=1).get(url, **request_kwargs)
    # Service is not up
    except requests.exceptions.ConnectionError:
        logger.error(
            f'Connection error! Is service at {url} up and running?'
        )
        is_down = True
    else:
        # Service is up but did not return 200 status code
        is_down = response.status_code >= 300
        if is_down:
            logger.warning(
                f'Service {url} is up but returned non 200 status. Caused by '
                f'{response.text}'
            )

    if exit_on_down and is_down:
        logger.info(f'Exiting program!')
        exit(1)

    return is_down


def json_to_key_path_value_list(filepath, var_prefix=None, delimiter=":"):
    """
    Convert JSON to a list of key path, value strings
    Prepend var_prefix to each key path if given

    For example this:
        {
            "database": {
                "type": "mongodb",
                "connection": "mongodb://vonkdb",
                "ports": [27017, 27000, 27001]
            }
        }

    gets converted to this:

        [
            "database:type=mongodb",
            "database:connection=mongodb://vonkdb",
            "database:ports:0=27017"
            "database:ports:1=27000"
            "database:ports:2=27001"
        ]
    :param filepath: path to JSON file
    :type filepath: str
    :param var_prefix: optional key path prefix
    :type var_prefix: str
    :param delimiter: key path delimiter
    :type delimiter: str
    :returns: list of strings
    """

    def lists_to_dicts(node):
        if isinstance(node, dict):
            for k, v in node.items():
                list_as_dict = {}
                if isinstance(v, list):
                    for i, vi in enumerate(v):
                        list_as_dict[i] = vi
                        lists_to_dicts(vi)
                    node[k] = list_as_dict
                lists_to_dicts(v)

    def dict_path(delimiter, path_prefix, path, data_dict, output_paths):
        for k, v in data_dict.items():
            if isinstance(v, dict):
                dict_path(
                    delimiter,
                    path_prefix, f'{path}{delimiter}{k}', v, output_paths
                )
            else:
                output_paths.append(
                    path_prefix +
                    f'{path}{delimiter}{k}'.lstrip(delimiter) +
                    f'={v}'
                )

    var_prefix = var_prefix or ''
    data = read_json(filepath)
    data_copy = deepcopy(data)
    env_var_strings = []

    lists_to_dicts(data_copy)
    dict_path(delimiter, var_prefix, '', data_copy, env_var_strings)

    return env_var_strings


def settings_diff(settings_filepath, default_settings_filepath,
                  output_filepath=None, var_prefix=None):
    """
    Used to generate the server settings that changed as compared to the
    default. Outputs changed settings in the form of environment variable
    strings

    Compares two lists produced by json_to_key_path_value_list and
    outputs the items in the first list that are not in the second
    list
    """
    settings_env_vars = json_to_key_path_value_list(settings_filepath,
                                                    var_prefix=var_prefix)
    default_env_vars = set(
        json_to_key_path_value_list(default_settings_filepath,
                                    var_prefix=var_prefix)
    )
    changed = [val for val in settings_env_vars
               if val not in default_env_vars]

    return sorted(changed)
