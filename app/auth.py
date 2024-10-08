from jose import JWTError, jwt
from fastapi.security.oauth2 import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
import os.path
from google.auth import default
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
import json
import secrets

# Cargar credenciales de Google desde el archivo JSON
with open("config/client_secret.json") as f:
    google_creds = json.load(f)

# Configuración de OAuth2 con Google
oauth = OAuth()
oauth.register(
    name="google",
    client_id=google_creds["web"]["client_id"],  # Cargamos el Client ID desde el JSON
    client_secret=google_creds["web"]["client_secret"],  # Cargamos el Client Secret desde el JSON
    authorize_url=google_creds["web"]["auth_uri"],  # URL de autorización desde el JSON
    authorize_params=None,
    access_token_url=google_creds["web"]["token_uri"],  # URL del token desde el JSON
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",  # JWKS URI set manually
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={"scope": "openid profile email"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Generate a 32-byte random key

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
def get_decode(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_gcp_credentials(credentials_file=None):
    """
    Retrieves GCP credentials to initialize the Vertex AI client.
    """
    try:
        if credentials_file and os.path.exists(credentials_file):
            print(f"Using credentials file: {credentials_file}")
            credentials = service_account.Credentials.from_service_account_file(credentials_file)
        else:
            print("Using default credentials")
            credentials, _ = default()
        return credentials
    except FileNotFoundError as e:
        print(f"Credentials file '{credentials_file}' not found.")

    except DefaultCredentialsError as e:
        print("Unable to obtain default credentials. Ensure that the environment "
                                    "is properly configured.")
        return None
