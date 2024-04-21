
import boto3

def create_music_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1') 

    table = dynamodb.create_table(
        TableName='Music',
        KeySchema=[
            {
                'AttributeName': 'title',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'artist',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'title',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'artist',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table

if __name__ == '__main__':
    music_table = create_music_table()
    print("Table status:", music_table.table_status)