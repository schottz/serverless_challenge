import json
import boto3
from moto import mock_aws
from handler import create_todo, get_todo, update_todo, delete_todo

TABLE_NAME = 'todo-list'

def initDb():
    dynamodb = boto3.resource('dynamodb', region_name='sa-east-1')
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    return dynamodb, table

@mock_aws
def test_create_todo():
    dynamodb = initDb()
    event = {'body': json.dumps({'title': 'New Todo', 'completed': False, 'metadata': {}})}
    result = create_todo(event, None)
    print("Create Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 201
    assert body['title'] == 'New Todo'
    assert body['completed'] is False

@mock_aws
def test_get_todo():
    dynamodb, table = initDb()
    table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = get_todo(event, None)
    print("Get Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Sample Todo'

@mock_aws
def test_update_todo():
    dynamodb, table = initDb()
    table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}, 'body': json.dumps({'title': 'Updated Todo', 'completed': True, 'metadata': {}})}
    result = update_todo(event, None)
    print("Update Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Updated Todo'

@mock_aws
def test_delete_todo_completed():
    dynamodb, table = initDb()
    table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': True, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    print("Delete Todo Completed Result:", result)
    assert result['statusCode'] == 204

@mock_aws
def test_delete_todo_not_completed():
    dynamodb, table = initDb()
    table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    print("Delete Todo Not Completed Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 400
    assert body['error'] == 'Todo must be completed to be deleted'
