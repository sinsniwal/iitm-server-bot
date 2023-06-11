from typing import TypedDict

class OpenIdConfig(TypedDict):
    issuer: str
    authorization_endpoint: str
    device_authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    revocation_endpoint: str
    jwks_uri: str
    response_types_supported: list[str]
    subject_types_supported: list[str]
    id_token_signing_alg_values_supported: list[str]
    scopes_supported: list[str]
    token_endpoint_auth_methods_supported: list[str]
    claims_supported: list[str]
    code_challenge_methods_supported: list[str]
    grant_types_supported: list[str]
