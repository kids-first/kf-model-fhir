import os
import re
from pprint import pprint

from kf_model_fhir.client import FhirApiClient
from kf_model_fhir.loader import load_resources

FHIR_USER = os.getenv("FHIR_USER")
FHIR_PASS = os.getenv("FHIR_PASS")
BASE_URL = os.getenv("FHIR_API")
FHIR_VERSION = '4.0.0'

def send_resource(payload):
    resource_type = payload.get('resourceType')
    endpoint = f"{client.base_url}/{resource_type}/{payload['id']}"
    success, result = client.send_request('PUT', endpoint, json=payload)
    return success, result, payload


client = FhirApiClient(base_url=BASE_URL, fhir_version=FHIR_VERSION, auth=(FHIR_USER, FHIR_PASS))


def camelsnake(text):
    regex1 = re.compile(r'([A-Z]+)([A-Z][a-z])')
    regex2 = re.compile(r'([a-z\d])([A-Z])')
    return regex2.sub(r'\1_\2', regex1.sub(r'\1_\2', text)).lower()

rd_list = [
    rd for rd in load_resources(os.path.join("site_root", "source", "resources"))
    if rd["resource_type"] == "StructureDefinition" 
    and rd["content"].get("baseDefinition", "").endswith("/StructureDefinition/Extension")
    and rd["content"].get("kind", "") == "complex-type"
]

types = {
    f"Extension.{x}": v for x, v in {
        # Primitive Types

        "valueBase64Binary": "string",
        "valueBoolean": "string",
        "valueCanonical": "uri",
        "valueCode": "token",
        "valueDate": "date",
        "valueDateTime": "date",
        "valueDecimal": "number",
        "valueId": "string",
        "valueInstant": "date",
        "valueInteger": "number",
        "valueMarkdown": "string",
        "valueOid": "uri",
        "valuePositiveInt": "number",
        "valueString": "string",
        "valueTime": "date",
        "valueUnsignedInt": "number",
        "valueUri": "uri",
        "valueUrl": "uri",
        "valueUuid": "uri",

        # Data Types

        # "valueAddress": "special",
        "valueAge": "quantity",
        # "valueAnnotation": "special",
        # "valueAttachment": "special",
        "valueCodeableConcept": "token",
        "valueCoding": "token",
        # "valueContactPoint": "special",
        # "valueCount": "number",
        # "valueDistance": "quantity",
        # "valueDuration": "quantity",
        # "valueHumanName": "string",
        # "valueIdentifier": "reference",
        # "valueMoney": "quantity",
        # "valuePeriod": "quantity",
        # "valueQuantity": "quantity",
        # "valueRange": "composite",
        # "valueRatio": "composite",
        # "valueReference": "reference",
        # "valueSampledData": "special",
        # "valueSignature": "special",
        # "valueTiming": "special",

        # MetaData Types

        # "valueContactDetail": "special",
        # "valueContributor": "special",
        # "valueDataRequirement": "special",
        # "valueExpression": "string",
        # "valueParameterDefinition": "special",
        # "valueRelatedArtifact": "special",
        # "valueTriggerDefinition": "special",
        # "valueUsageContext": "special",

        # Special Types
    
        # "valueDosage": "quantity",
        # "valueMeta": "special",

    }.items()
}

sp = []

for rd in rd_list:
    elements = rd["content"]["differential"]["element"]
    for e in elements:
        type = e["id"]
        if type in types:
            id = camelsnake(rd["content"]["id"])
            name = camelsnake(rd["content"]["name"])
            if len(rd["content"]["context"]) > 1:  # probably wrong
                continue  # probably wrong
            base = rd["content"]["context"][0]["expression"]  # probably wrong
            sp.append({
                "resourceType": "SearchParameter",
                "url": f"http://fhir.kids-first.io/SearchParameter/{id}",
                "name": id,
                "id": id,
                "status": "active",
                "experimental": True,
                "publisher": "Kids First DRC",
                "description": f"Search {base} by {name}",
                "code": name,
                "base": [
                    base
                ],
                "type": types[type],
                "expression": f"{base}.extension.where(url = 'http://fhir.kids-first.io/StructureDefinition/{name}').value",
                "target": [
                    base
                ]
            })

for p in sp:
    pprint(send_resource(p))
    print()
