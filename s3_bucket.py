import boto3

def create_s3_bucket(bucket_name, region='us-east-1'):
    """
    Create an S3 bucket with the specified name in the specified region.
    """
    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' created successfully.")
    except Exception as e:
        print(f"Error creating S3 bucket '{bucket_name}': {e}")

if __name__ == "__main__":
    bucket_name = "s3bucket-artist-images"
    create_s3_bucket(bucket_name)
