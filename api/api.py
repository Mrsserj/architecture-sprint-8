import tornado.ioloop
import tornado.web
import json
import os
import jwt
import requests

from functools import wraps

# Переменные окружения для Keycloak
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "your_realm")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "your_client_id")
KEYCLOAK_PUBLIC_KEY_URL = os.environ.get("KEYCLOAK_PUBLIC_KEY_URL", "http://keycloak:8080/realms/your_realm/protocol/openid-connect/certs") # Укажите корректный URL

# Получение публичного ключа Keycloak
try:
    response = requests.get(KEYCLOAK_PUBLIC_KEY_URL)
    response.raise_for_status()  # Проверка на ошибки HTTP
    public_key = response.json()['keys'][0]['x5c'][0]
    public_key = f"-----BEGIN CERTIFICATE-----n{public_key}n-----END CERTIFICATE-----"
except requests.exceptions.RequestException as e:
    print(f"Error fetching public key from Keycloak: {e}")
    public_key = None  # Или обработка ошибки по-другому
except (KeyError, IndexError, TypeError) as e:
    print(f"Error parsing public key from Keycloak response: {e}")
    public_key = None  # Или обработка ошибки по-другому


def auth_required(handler_method):
    @wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get("Authorization")

        if not auth_header:
            self.set_status(401)
            self.finish({"error": "Authorization header missing"})
            return

        try:
            token = auth_header.split(" ")[1]  # Bearer <token>
            decoded_token = verify_token(token)

            if not decoded_token:
                self.set_status(401)
                self.finish({"error": "Invalid token"})
                return

            # Проверка роли
            if "resource_access" in decoded_token and KEYCLOAK_CLIENT_ID in decoded_token["resource_access"]:
                roles = decoded_token["resource_access"][KEYCLOAK_CLIENT_ID].get("roles", [])
                if "prothetic_user" not in roles:
                    self.set_status(403)  # Forbidden
                    self.finish({"error": "Insufficient permissions"})
                    return
            else:
                self.set_status(403)
                self.finish({"error": "Insufficient permissions"})
                return

        except Exception as e:
            print(f"Authentication error: {e}")
            self.set_status(401)
            self.finish({"error": "Authentication failed"})
            return

        return handler_method(self, *args, **kwargs)

    return wrapper


def verify_token(token):
    """
    Верификация токена с использованием публичного ключа Keycloak.
    """
    if not public_key:
        print("Public key is not available, cannot verify token.")
        return None

    try:
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],  # Укажите используемый алгоритм
            options={"verify_exp": True} # Проверка срока действия
        )
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None


class ReportsHandler(tornado.web.RequestHandler):
    @auth_required
    def get(self):
        # Здесь генерируется произвольный отчет
        report_data = {"report_type": "example", "data": ["item1", "item2"]}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(report_data))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/reports", ReportsHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    port = int(os.environ.get("PORT", 8000))
    app.listen(port)
    print(f"Listening on port {port}")
    tornado.ioloop.IOLoop.current().start()
