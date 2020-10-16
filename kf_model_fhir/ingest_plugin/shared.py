import os
import re
from pprint import pformat

from kf_lib_data_ingest.common import constants
from ncpi_fhir_utility.client import FhirApiClient
from requests import RequestException


def not_none(val):
    assert val is not None
    return val


# http://hl7.org/fhir/R4/datatypes.html#id
def make_id(*args):
    return re.sub(r"[^A-Za-z0-9\-\.]", "-", ".".join(str(a) for a in args))[:64]


def flexible_age(record, days_concept, generic_concept):
    age = record.get(days_concept)
    units = record.get(generic_concept.UNITS)
    value = record.get(generic_concept.VALUE)

    if (age is None) and (units is not None) and (value is not None):
        if units == constants.AGE.UNITS.DAYS:
            age = int(value)
        elif units == constants.AGE.UNITS.MONTHS:
            age = int(value * 30.44)
        elif units == constants.AGE.UNITS.YEARS:
            age = int(value * 365.25)

    return age


FHIR_USER = os.getenv("FHIR_USER") or "admin"
FHIR_PW = os.getenv("FHIR_PW") or "password"
clients = {}


def submit(host, entity_class, body):
    clients[host] = clients.get(host) or FhirApiClient(
        base_url=host, auth=(FHIR_USER, FHIR_PW)
    )

    # drop empty fields
    body = {k: v for k, v in body.items() if v not in (None, [], {})}

    verb = "POST"
    api_path = f"{host}/{entity_class.resource_type}"
    if body.get("id"):
        verb = "PUT"
        body["id"] = make_id(body["id"])
        api_path = f"{api_path}/{body['id']}"
        if "patches" in body:
            verb = "PATCH"
            body = body["patches"]

    cheaders = clients[host]._fhir_version_headers()
    if verb == "PATCH":
        cheaders["Content-Type"] = cheaders["Content-Type"].replace(
            "application/fhir", "application/json-patch"
        )

    success, result = clients[host].send_request(
        verb, api_path, json=body, headers=cheaders
    )

    if (
        (not success)
        and (verb == "PUT")
        and (
            "no resource with this ID exists"
            in result.get("response", {})
            .get("issue", [{}])[0]
            .get("diagnostics", "")
        )
    ):
        verb = "POST"
        api_path = f"{host}/{entity_class.resource_type}"
        success, result = clients[host].send_request(
            verb, api_path, json=body, headers=cheaders
        )

    if success:
        return result["response"]["id"]
    else:
        raise RequestException(
            f"Sent {verb} request to {api_path}:\n{pformat(body)}"
            f"\nGot:\n{pformat(result)}"
        )
