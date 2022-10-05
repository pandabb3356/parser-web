import msal

from typing import NamedTuple


class MSUser(NamedTuple):
    name: str
    email: str


class MSALApp:
    def __init__(
        self, client_id, client_secret, authority, redirect_uri, scopes=None, cache=None
    ):

        self.scopes = scopes or []
        self.redirect_uri = redirect_uri

        self.app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
            token_cache=cache,
        )

    def init_auth_code_flow(self, state=None, redirect_uri=None):
        return self.app.initiate_auth_code_flow(
            self.scopes,
            state=state,
            redirect_uri=redirect_uri or self.redirect_uri,
        )

    def get_token_by_auth_code_flow(self, auth_response, flow):
        result = self.app.acquire_token_by_auth_code_flow(
            flow,
            auth_response,
        )

        return result

    @classmethod
    def init_user_from_id_token_claims(cls, id_token_claims: dict) -> MSUser:
        return MSUser(name=id_token_claims.get("name") or "", email=id_token_claims.get("email") or "")


def get_microsoft_settings(app):
    return app.config.get("MICROSOFT_SETTINGS") or {}


def init_msal_app(app):
    microsoft_settings = get_microsoft_settings(app)
    return MSALApp(
        client_id=microsoft_settings.get("client_id"),
        client_secret=microsoft_settings.get("client_secret"),
        authority=microsoft_settings.get("authority"),
        redirect_uri=microsoft_settings.get("redirect_uri"),
        scopes=microsoft_settings.get("scopes") or [],
    )
