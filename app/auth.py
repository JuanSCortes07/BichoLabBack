from jose import JWTError, jwt
from fastapi.security.oauth2 import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
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
