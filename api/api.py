import logging
import tornado.ioloop
import tornado.web
import json
import os
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

from functools import wraps

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Переменные окружения для Keycloak
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "reports-realm")
KEYCLOAK_CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "reports-api")
KEYCLOAK_PUBLIC_KEY_URL = os.environ.get("KEYCLOAK_PUBLIC_KEY_URL", "http://127.0.0.1:8080/realms/reports-realm/protocol/openid-connect/certs") # Укажите корректный URL
JWKS = None


def get_keycloal_public_key():
    # Получение публичного ключа Keycloak
    try:
        response = requests.get(KEYCLOAK_PUBLIC_KEY_URL)
        response.raise_for_status()  # Проверка на ошибки HTTP
        jwks = response.json()['keys']
    except requests.exceptions.RequestException as e:
        logger.debug(f"Error fetching public key from Keycloak: {e}")
        jwks = None  # Или обработка ошибки по-другому
    except (KeyError, IndexError, TypeError) as e:
        logger.debug(f"Error parsing public key from Keycloak response: {e}")
        jwks = None  # Или обработка ошибки по-другому
    return jwks


def rsa_key_from_jwk(jwk):
    """
    Convert jwk to rsa key
    """
    exponent = jwk.get("e")
    modulus = jwk.get("n")

    if not exponent or not modulus:
        raise Exception("Invalid JWK format")

    # Convert the data from strings to integers
    exponent_int = int.from_bytes(base64.urlsafe_b64decode(exponent + '=' * (4 - len(exponent) % 4)), 'big')
    modulus_int = int.from_bytes(base64.urlsafe_b64decode(modulus + '=' * (4 - len(modulus) % 4)), 'big')

    # Create public key
    public_key = rsa.RSAPublicNumbers(exponent_int, modulus_int).public_key(default_backend())
    return public_key


def auth_required(handler_method):
    @wraps(handler_method)
    def wrapper(self, *args, **kwargs):
        global JWKS
        auth_header = self.request.headers.get("Authorization")
        if not JWKS:
            JWKS = get_keycloal_public_key()

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
            if "realm_access" in decoded_token:
                roles = decoded_token["realm_access"].get("roles", [])
                if "prothetic_user" not in roles:
                    self.set_status(403)  # Forbidden
                    self.finish({"error": "Insufficient permissions"})
                    return
            else:
                self.set_status(403)
                self.finish({"error": "Insufficient permissions"})
                return

        except Exception as e:
            logger.debug(f"Authentication error: {e}")
            self.set_status(401)
            self.finish({"error": "Authentication failed"})
            return

        return handler_method(self, *args, **kwargs)

    return wrapper


def verify_token(token):
    """
    Верификация токена с использованием JWKS Keycloak.
    """
    if not JWKS:
        logger.debug("JWKS is not available, cannot verify token.")
        return None

    try:
        # Получаем header токена (не декодируем payload)
        headers = jwt.get_unverified_header(token)
        logger.debug(f"JWT headers: {headers}")
        kid = headers.get("kid")
        alg = headers.get("alg")

        if not kid:
            logger.debug("No 'kid' found in token header.")
            return None

        # Ищем ключ с соответствующим kid в JWKS
        key = None
        for k in JWKS:
            if k["kid"] == kid:
                key = k
                break

        if not key:
            logger.debug(f"No key found with kid '{kid}' in JWKS.")
            return None

        # Получаем публичный ключ в формате, необходимом для PyJWT
        if alg == "RS256":
            try:
                public_key = rsa_key_from_jwk(key)  # Use the function
            except Exception as e:
                logger.debug(f"Error getting rsa public key: {e}")
                return None
        else:
            logger.debug(f"Algorithm {alg} not supported")
            return None
        logger.debug(f"Public key: {public_key}")

        # Декодируем и верифицируем токен
        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=[headers["alg"]], # Берем алгоритм из header токена
            # audience=KEYCLOAK_CLIENT_ID,  # Проверяем audience (опционально, но рекомендуется)
            options={"verify_exp": True}  # Проверка срока действия
        )
        return decoded_token
    except jwt.ExpiredSignatureError:
        logger.debug("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.debug(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.debug(f"Error decoding token: {e}")
        return None


class CustomRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # Разрешить запросы с любого домена
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, authorization")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        

class ReportsHandler(CustomRequestHandler):
    @auth_required
    def get(self):
        # Здесь генерируется произвольный отчет
        report_data = {"report_type": "example", "data": ["item1", "item2"]}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(report_data))

    def options(self):  # Обработчик OPTIONS
        self.set_status(204)
        self.finish()



class MainHandler(CustomRequestHandler):
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
    logger.debug(f"Listening on port {port}")
    tornado.ioloop.IOLoop.current().start()
