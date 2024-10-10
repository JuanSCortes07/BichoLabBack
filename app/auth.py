import os.path
from google.auth import default
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError


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
