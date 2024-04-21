import boto3
import json
import requests
from io import BytesIO
from PIL import Image

# Function to download image from URL
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

# Function to upload image to S3
def upload_image_to_s3(image, bucket_name, object_key):
    s3 = boto3.client('s3')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')  # Adjust format if needed
    buffer.seek(0)
    s3.upload_fileobj(buffer, bucket_name, object_key)

if __name__ == "__main__":
    # Load data from a1.json
    with open('a1.json') as json_file:
        data = json.load(json_file)
        music_data = data['songs']

        # Initialize S3 client
        s3_bucket_name = "s3bucket-artist-images"

        for music in music_data:
            # Extract image URL
            image_url = music['img_url']

            # Download image
            image = download_image(image_url)

            if image:
                # Upload image to S3
                object_key = f"{music['artist']}.jpg"  # Set object key as artist name
                upload_image_to_s3(image, s3_bucket_name, object_key)
                print(f"Uploaded image for artist {music['artist']}")
            else:
                print(f"Failed to download image for artist {music['artist']}")
