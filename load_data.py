import boto3
import json

def load_music_data(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
    table = dynamodb.Table('Music')

    with open('a1.json') as json_file:
        data = json.load(json_file)
        music_data = data['songs']  # Access the 'songs' key in the JSON data

        for music in music_data:
            title = music['title'].lower()
            artist = music['artist'].lower()
            year = music['year']
            web_url = music['web_url']
            image_url = music['img_url'] 
            table.put_item(Item={
                'title': title,
                'artist': artist,
                'year': year,
                'web_url': web_url,
                'image_url': image_url
            })
            print(f"Added music: {title} - {artist}")

if __name__ == '__main__':
    load_music_data()