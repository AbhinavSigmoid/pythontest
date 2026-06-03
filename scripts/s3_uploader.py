import boto3


BUCKET_NAME = "sigma-datatech-abhi"


def upload_file(
    file_path,
    object_name=None
):

    if object_name is None:

        object_name = file_path.split("/")[-1]

    s3 = boto3.client("s3")

    s3.upload_file(
        file_path,
        BUCKET_NAME,
        object_name
    )

    print(
        f"Uploaded {object_name}"
    )