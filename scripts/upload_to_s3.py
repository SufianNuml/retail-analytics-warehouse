import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the S3 client using credentials from .env
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
RAW_DATA_PATH = 'data/raw'
S3_RAW_PREFIX = 'raw/'

def upload_raw_files():
    """Upload all CSV files from local data/raw/ to S3 raw/ zone."""

    print("=" * 50)
    print("Starting S3 Upload — Raw Zone")
    print("=" * 50)

    files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith('.csv')]

    if not files:
        print("ERROR: No CSV files found in data/raw/. Did you run generate_data.py?")
        return

    uploaded_count = 0

    for filename in files:
        local_path = os.path.join(RAW_DATA_PATH, filename)
        s3_key = S3_RAW_PREFIX + filename

        file_size = os.path.getsize(local_path)
        file_size_kb = round(file_size / 1024, 2)

        print(f"\nUploading: {filename}")
        print(f"  Local path : {local_path}")
        print(f"  S3 path    : s3://{BUCKET_NAME}/{s3_key}")
        print(f"  File size  : {file_size_kb} KB")

        try:
            s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
            print(f"  Status     : SUCCESS")
            uploaded_count += 1
        except Exception as e:
            print(f"  Status     : FAILED — {str(e)}")

    print("\n" + "=" * 50)
    print(f"Upload complete. {uploaded_count}/{len(files)} files uploaded successfully.")
    print("=" * 50)

if __name__ == "__main__":
    upload_raw_files()