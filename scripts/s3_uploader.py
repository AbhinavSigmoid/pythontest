import os
import boto3
from dotenv import load_dotenv
import streamlit as st

load_dotenv(override=True)


def get_env_var(key):
    try:
        import streamlit as st
        return os.getenv(key) or st.secrets.get(key)
    except Exception:
        return os.getenv(key)


def get_s3_client():

    aws_access_key = (
        os.getenv("AWS_ACCESS_KEY_ID")
        or st.secrets.get("AWS_ACCESS_KEY_ID")
    )

    aws_secret_key = (
        os.getenv("AWS_SECRET_ACCESS_KEY")
        or st.secrets.get("AWS_SECRET_ACCESS_KEY")
    )

    region = (
        os.getenv("AWS_REGION")
        or st.secrets.get("AWS_REGION")
    )

    if aws_access_key and aws_secret_key:

        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region,
        )

    return boto3.client("s3")


def upload_file(file_path, object_name=None):

    bucket_name = get_env_var("AWS_BUCKET_NAME")

    if not bucket_name:
        raise ValueError("AWS_BUCKET_NAME not configured")

    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = get_s3_client()

    s3_client.upload_file(
        file_path,
        bucket_name,
        object_name
    )

    print(
        f"Successfully uploaded {file_path} "
        f"to S3 bucket '{bucket_name}' "
        f"as '{object_name}'"
    )

    return True


def list_s3_files():

    bucket_name = get_env_var("AWS_BUCKET_NAME")

    if not bucket_name:
        return []

    try:

        s3_client = get_s3_client()

        response = s3_client.list_objects_v2(
            Bucket=bucket_name
        )

        contents = response.get(
            "Contents",
            []
        )

        return [
            obj["Key"]
            for obj in contents
            if obj["Key"].endswith(".pdf")
        ]

    except Exception as e:

        print(
            f"Error listing S3 files: {e}"
        )

        return []


def download_file_from_s3(
    file_name,
    local_path
):

    bucket_name = get_env_var(
        "AWS_BUCKET_NAME"
    )

    if not bucket_name:
        raise ValueError(
            "AWS_BUCKET_NAME not configured"
        )

    s3_client = get_s3_client()

    s3_client.download_file(
        bucket_name,
        file_name,
        local_path
    )

    print(
        f"Downloaded {file_name} "
        f"to {local_path}"
    )

    return True


if __name__ == "__main__":

    test_file = "uploads/demo.pdf"

    if os.path.exists(test_file):

        upload_file(test_file)

        print(
            "S3 TEST SUCCESS"
        )

    else:

        print(
            f"File not found: {test_file}"
        )