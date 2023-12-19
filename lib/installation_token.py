import jwt
import requests
from datetime import datetime, timedelta, timezone


def generate_jwt(app_id, private_key_path):
    now = datetime.now(timezone.utc)
    with open(private_key_path, "rb") as pem_file:
        signing_key = jwt.jwk_from_pem(pem_file.read())

    iat = int((now).timestamp())
    expiration_date = int((now + timedelta(seconds=300)).timestamp())

    payload = {
        "iat": iat,
        "exp": expiration_date,
        "iss": app_id,
    }

    jwt_instance = jwt.JWT()
    encoded_jwt = jwt_instance.encode(payload, signing_key, alg="RS256")
    return encoded_jwt


def generate_installation_token(jwt_token, installation_id):
    response = requests.post(
        "https://api.github.com/app/installations/"
        f"{installation_id}/access_tokens",
        headers={
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    return response.json()
