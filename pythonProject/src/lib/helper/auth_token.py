import base64
import hashlib
import random
import string
from typing import Any
import requests
from oauthlib.oauth2 import WebApplicationClient
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os


class OAuthHttpServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.authorization_code = ""


class OAuthHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write("<script type=\"application/javascript\">window.close();</script>".encode("UTF-8"))

        parsed = parse.urlparse(self.path)
        qs = parse.parse_qs(parsed.query)

        self.server.authorization_code = qs["code"][0]


def generate_code() -> tuple[str, str]:
    rand = random.SystemRandom()
    code_verifier = ''.join(rand.choices(string.ascii_letters + string.digits, k=128))

    code_sha_256 = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    b64 = base64.urlsafe_b64encode(code_sha_256)
    code_challenge = b64.decode('utf-8').replace('=', '')

    return (code_verifier, code_challenge)


def login(config: dict[str, Any]) -> str:
    with OAuthHttpServer(('', config["port"]), OAuthHttpHandler) as httpd:
        client = WebApplicationClient(config["client_id"])

        code_verifier, code_challenge = generate_code()

        auth_uri = client.prepare_request_uri(
            config["auth_uri"],
            redirect_uri=config["redirect_uri"],
            scope=config["scopes"],
            state="test_doesnotmatter",
            code_challenge=code_challenge,
            code_challenge_method="S256")

        service_obj = Service(config["chrome_driver_path"])
        driver = webdriver.Chrome(service=service_obj)
        driver.implicitly_wait(10)
        driver.get(auth_uri)
        # enter username
        username_elem = driver.find_element(By.ID, "okta-signin-username")
        username_elem.send_keys(config["username"])
        username_elem.send_keys(Keys.RETURN)
        # enter password
        password_elem = driver.find_element(By.ID, "input59")
        password_elem.send_keys(config["password"])
        password_elem.send_keys(Keys.RETURN)

        httpd.handle_request()

        auth_code = httpd.authorization_code

        driver.close()

        data = {
            "code": auth_code,
            "client_id": config["client_id"],
            "grant_type": "authorization_code",
            "scopes": config["scopes"],
            "redirect_uri": config["redirect_uri"],
            "code_verifier": code_verifier
        }

        response = requests.post(config["token_uri"], data=data, verify=True)
        access_token = response.json()["access_token"]
        return access_token


if __name__ == "__main__":
    config = {
        "auth_uri": "https://smileco.oktapreview.com/oauth2/v1/authorize",
        "token_uri": "https://smileco.oktapreview.com/oauth2/v1/token",
        "port": 8080,
        "client_id": "0oa1bmtqbulBan6PL0h8",
        "scopes": "openid profile email",
        "redirect_uri": "http://localhost:8080/login/callback",
        "username": os.environ["OKTA_USERNAME"],
        "password": os.environ["OKTA_PASSWORD"],
        "chrome_driver_path": "/Users/cliff.lehr/PycharmProjects/finance-service/tests/Orion/src/lib/helpers/chromedriver"
    }
    access_token = login(config)
    print(access_token)
