# FHIR Security

https://www.hl7.org/fhir/security.html#6.1.0

## Authentication
Based on OAuth 2 with OIDC

## Authorization
Based on OAuth 2

## SMART on FHIR
- SMART on FHIR = another set of auth standards on top of OAuth 2 + OIDC,
  specifically for FHIR apps and services.

SMART App Launch Framework
---------------------------
http://www.hl7.org/fhir/smart-app-launch/

- These guidelines cover authentication and authorization standards for
  OAuth 2 client apps (Single-Page, Server-Side, Native, Mobile) that want to
  access protected resources on a FHIR resource server
- The OAuth 2 Resource Server in this case is a FHIR resource server

\* Many of these guidelines seem to be specifically for an
EHR Authorization Server and EHR FHIR resource server

SMART on FHIR Backend Service
-----------------------------
https://hl7.org/fhir/uv/bulkdata/authorization/index.html

- These guidelines cover authentication and authorization standards
  for an API/service that wants to access protected resources on a
  FHIR resource server.
- The OAuth 2 Resource Server in this case is the FHIR resource server
- The API would take the role of "client" in the OAuth 2 client credentials
  flow
- If the client is a backend service, SMART standard requires that the client
  authenticate with the FHIR authorization server using private key JWT
  authentication which uses an asymmetric key pair for token validation
- SMART standard recommends that the client be registered using dynamic client
  registration

Private Key JWT Authentication
-------------------------------
- Client generates public/private key pair
- Client creates an OIDC JWT
- Client signs JWT with private key
- Client must publish its public key
- Authz server must verify signature with client's public key

Dynamic Client Registration
----------------------------
https://auth0.com/docs/api-auth/dynamic-client-registration
- Dynamic/run time registration of 3rd party clients
- Allows one to setup the authentication method between the Authorization
server and the client (private key JWT auth vs client id, secret basic)


Authorization Capability Discovery
----------------------------------
http://www.hl7.org/fhir/smart-app-launch/conformance/index.html#request

- A FHIR resource server that conforms to "SMART standards", will advertise
its authorization endpoints via `/.well-known/smart-configuration`

For example:

```
GET fhir.ehr.example.com/.well-known/smart-configuration

Returns:
{
  "authorization_endpoint": "https://ehr.example.com/auth/authorize",
  "token_endpoint": "https://ehr.example.com/auth/token",
  "token_endpoint_auth_methods_supported": ["client_secret_basic"],
  "registration_endpoint": "https://ehr.example.com/auth/register",
  "scopes_supported": ["openid", "profile", "launch", "launch/patient", "patient/*.*", "user/*.*", "offline_access"],
  "response_types_supported": ["code", "code id_token", "id_token", "refresh_token"],
  "management_endpoint": "https://ehr.example.com/user/manage"
  "introspection_endpoint": "https://ehr.example.com/user/introspect"
  "revocation_endpoint": "https://ehr.example.com/user/revoke",
  "capabilities": ["launch-ehr", "client-public", "client-confidential-symmetric", "context-ehr-patient", "sso-openid-connect"]
}
```

These endpoints tell clients everything they need to know in order to
authenticate with the Authorization server, fetch access tokens, and know
which permissions (scopes) are supported by the resource server

## SMART on FHIR Scopes
- A scope specifies operation(s) that can be performed on specific
FHIR resource(s).
- A scope has a context - `patient`, `user`

The 2 common scopes are:
1. `patient/*.read`
    - Read any resource for the current patient
    - Patient-specific scopes allow access to specific data about a
      single patient - this is relevant to an EHR app scenario where you
      launch an app with a single patient context bc you're launching the app
      to explore only that patient's EHR.
2. `user/*.*`
    - Permission to read and write all resources that the current user can
      access

## Role-Based Access Control (RBAC)
- Permissions are operations on an object that a user wishes to access.
- FHIR naturally enables RBAC
- Objects = FHIR resources
- Operations = CRUDE (Create, Read, Update, Delete, Execute)
- Role = set of permitted operations on set of resources
- Users get assigned roles

## Attribute-Based Access Control (ABAC).
- User requests to perform operations on objects. Request is granted or denied
based on a set of access control policies that are specified in terms of
attributes and conditions.
- Objects = FHIR resources
- Operations = CRUDE (Create, Read, Update, Delete, Execute)
- Attributes =
    - Security label/tags on an object
    - Other object attributes (e.g. author, confidentiality)
    - Requesting user characteristics (e.g. relation to patient, role)
    - Transaction context (e.g. purpose of use)

## FHIR Security Labels
- Represented as a FHIR Coding (has a system, code, and display)
```
{
 "id" : "patient-1",
 "meta" : {
   "security" : [{
     "system" : "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
     "code" : "R",
     "display" : "Restricted"
   }]
 }
 ... other content etc.....
}
```
- Core security labels are defined by HL7 Healthcare Classification System (HCS)
    - Purpose of use
    - Confidentiality codes
    - Control of flow

## FHIR Compartments
- TODO
