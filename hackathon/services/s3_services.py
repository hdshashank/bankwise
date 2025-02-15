import boto3
import uuid

# Directly add AWS credentials
AWS_ACCESS_KEY_ID = " key_id"
AWS_SECRET_ACCESS_KEY = " access_key"
AWS_REGION = "region"
S3_BUCKET_NAME = "name"

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

def upload_to_s3(file, filename):
    """Uploads a file to S3 and returns the file URL."""
    file_key = f"uploads/{uuid.uuid4()}_{filename}"
    
    s3.upload_fileobj(
        file,
        S3_BUCKET_NAME,
        file_key,
        ExtraArgs={"ContentType": "application/pdf", "ACL": "public-read"},
    )

    return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"
