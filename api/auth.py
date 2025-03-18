import jwt
from keycloak import KeycloakOpenID


class IAMClient:
    def __init__(self, keycloak_server_url, realm_name, client_id, client_secret):
        self.client = KeycloakOpenID(
            server_url=keycloak_server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret,
        )

        self.public_key = f"-----BEGIN PUBLIC KEY-----\n{self.client.public_key()}\n-----END PUBLIC KEY-----"

    def get_roles(self, token: str):
        try:
            payload = jwt.decode(token, self.public_key, algorithms=["RS256"])
            roles = payload["realm_access"]["roles"]
            return 0, roles
        except jwt.ExpiredSignatureError:
            return 1, {}
        except jwt.InvalidTokenError:
            return 2, {}
 
        return 3, {}  # unknown error