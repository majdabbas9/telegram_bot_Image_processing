import boto3
import subprocess
import sys
import logging
import argparse
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def fetch_secrets(secret_name, region):
    """Fetch secrets from AWS Secrets Manager."""
    logging.info(f"🔐 Fetching secrets from AWS Secrets Manager: {secret_name} in region {region}")
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secrets = json.loads(response["SecretString"])
        logging.info(f"✅ Successfully fetched secrets: {list(secrets.keys())}")
        return secrets
    except Exception as e:
        logging.exception(f"❌ Failed to fetch secrets: {e}")
        sys.exit(1)

def build_and_push_image(image_name, secrets):
    """Build and push Docker image with secrets as build args."""
    logging.info(f"🐳 Starting Docker build and push for image: {image_name}")
    telegram_token = secrets.get("telegram_token", "")
    sqs_url = secrets.get("sqs_queue_url", "")
    s3_bucket_id = secrets.get("s3_bucket_id", "")

    build_command = [
        "docker", "build", ".", "--push",
        "-t", image_name,
        "--build-arg", f"TELEGRAM_TOKEN={telegram_token}",
        "--build-arg", f"SQS_URL={sqs_url}",
        "--build-arg", f"S3_BUCKET_ID={s3_bucket_id}"
    ]

    logging.info(f"📦 Running Docker command: {' '.join(build_command)}")

    try:
        result = subprocess.run(build_command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"❌ Docker build failed:\n{result.stderr}")
            sys.exit(1)
        else:
            logging.info(f"✅ Docker build and push successful:\n{result.stdout}")
    except Exception as e:
        logging.exception(f"❌ Exception during Docker build: {e}")
        sys.exit(1)

def store_image_name_to_ssm(image_name, param_name, region):
    """Store image name in SSM Parameter Store."""
    logging.info(f"📝 Storing image name to AWS SSM Parameter Store: {param_name}")
    try:
        ssm = boto3.client("ssm", region_name=region)
        ssm.put_parameter(
            Name=param_name,
            Value=image_name,
            Type="String",
            Overwrite=True
        )
        logging.info(f"✅ Successfully stored image name to SSM: {param_name} = {image_name}")
    except Exception as e:
        logging.exception(f"❌ Failed to store image name to SSM: {e}")
        sys.exit(1)

def main():
    logging.info("🚀 Starting build_and_push script")

    parser = argparse.ArgumentParser(description="Build Docker image with secrets and save to SSM.")
    parser.add_argument("--region", required=True, help="AWS region")
    parser.add_argument("--secret-name", required=True, help="Secrets Manager name")
    parser.add_argument("--ssm-param", required=True, help="SSM parameter key")
    parser.add_argument("--image-name", required=True, help="Docker image name (with tag)")

    args = parser.parse_args()

    logging.info(f"📥 Parsed arguments:\n  Region: {args.region}\n  Secret Name: {args.secret_name}\n  SSM Param: {args.ssm_param}\n  Image Name: {args.image_name}")

    secrets = fetch_secrets(args.secret_name, args.region)
    build_and_push_image(args.image_name, secrets)
    store_image_name_to_ssm(args.image_name, args.ssm_param, args.region)

    logging.info("🎉 All steps completed successfully.")

if __name__ == "__main__":
    main()
