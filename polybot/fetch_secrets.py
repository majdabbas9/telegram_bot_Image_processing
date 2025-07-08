# polybot/secrets_loader.py
import os
import json
import base64
import logging
import boto3
from botocore.exceptions import ClientError

def fetch_secrets(secret_name, region):
    logging.info(f"🔐 Fetching secrets: {secret_name} in {region}")
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)

        if "SecretString" in response:
            secrets = json.loads(response["SecretString"])
        elif "SecretBinary" in response:
            secrets = json.loads(base64.b64decode(response["SecretBinary"]))
        else:
            raise ValueError("No secret string or binary found")

        logging.info(f"✅ Fetched secrets: {list(secrets.keys())}")
        return secrets
    except ClientError as e:
        logging.exception("❌ AWS ClientError during secret fetch")
        raise
    except Exception as e:
        logging.exception("❌ Unexpected error during secret fetch")
        raise

def load_secrets_into_env(secrets):
    for key, value in secrets.items():
        os.environ[key.upper()] = value
    logging.info(f"✅ Loaded secrets into env: {list(secrets.keys())}")