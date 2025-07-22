import logging
from google.cloud import secretmanager


def get_secret(secret_id, project_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    logging.info(f"Fetching secret from: {secret_name}")

    try:
        response = client.access_secret_version(name=secret_name)
        secret_value = response.payload.data.decode("UTF-8")
        logging.info(f"Secret '{secret_id}' retrieved successfully.")
        return secret_value
    except Exception as e:
        logging.error(f"Error accessing secret {secret_id}: {e}", exc_info=True)
        raise
