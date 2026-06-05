import os
import boto3
from dotenv import load_dotenv

# Load environment variables dynamically
load_dotenv(override=True)

def get_s3_client():
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    
    # If credentials are explicitly provided in .env, configure them
    if aws_access_key and aws_secret_key:
        return boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    # Otherwise, fallback to the default AWS credentials provider chain
    return boto3.client("s3")

def upload_file(file_path, object_name=None):
    """
    Uploads a file to the AWS S3 bucket specified in the environment (.env)
    """
    load_dotenv(override=True)
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("AWS_BUCKET_NAME is not set in the environment or .env file.")

    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = get_s3_client()
    s3_client.upload_file(file_path, bucket_name, object_name)
    print(f"Successfully uploaded {file_path} to S3 bucket '{bucket_name}' as '{object_name}'")
    return True

def list_s3_files():
    """
    List all file keys in the S3 bucket
    """
    load_dotenv(override=True)
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    if not bucket_name:
        return []
    try:
        s3_client = get_s3_client()
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        contents = response.get("Contents", [])
        # Only return keys ending in .pdf
        return [obj["Key"] for obj in contents if obj["Key"].endswith(".pdf")]
    except Exception as e:
        print(f"Error listing S3 files: {e}")
        return []

def download_file_from_s3(file_name, local_path):
    """
    Download a file from S3 to a local path
    """
    load_dotenv(override=True)
    bucket_name = os.getenv("AWS_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("AWS_BUCKET_NAME is not set in the environment or .env file.")
    s3_client = get_s3_client()
    s3_client.download_file(bucket_name, file_name, local_path)
    print(f"Downloaded {file_name} from S3 bucket '{bucket_name}' to '{local_path}'")
    return True

if __name__ == "__main__":
    import sys
    target_file = sys.argv[1] if len(sys.argv) > 1 else "uploads/demo.pdf"
    
    print(f"Testing S3 uploader with file: {target_file}")
    try:
        if os.path.exists(target_file):
            upload_file(target_file)
            print("UPLOAD SUCCESS")
        else:
            print(f"Test file not found: {target_file}")
    except Exception as e:
        print("UPLOAD FAILED")
        print(e)