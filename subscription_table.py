import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Define the table schema
table_name = 'subscription'
table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[
        {
            'AttributeName': 'user_email',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName': 'music_title',
            'KeyType': 'RANGE'  # Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'user_email',
            'AttributeType': 'S'  # String
        },
        {
            'AttributeName': 'music_title',
            'AttributeType': 'S'  # String
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait for the table to be created
print(f'Creating table {table_name}...')
table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
print(f'Table {table_name} created successfully!')


table = dynamodb.Table('subscription')

# Update the table to add the additional attributes
table.update(
    AttributeDefinitions=[
        {
            'AttributeName': 'artist',
            'AttributeType': 'S'  # String
        },
        {
            'AttributeName': 'year',
            'AttributeType': 'N'  # Number
        },
        {
            'AttributeName': 'image_url',
            'AttributeType': 'S'  # String
        },
        {
            'AttributeName': 'web_url',
            'AttributeType': 'S'  # String
        }
    ]
)

print('Table updated with additional attributes.')