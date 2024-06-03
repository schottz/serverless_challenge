import json
import pytest
import boto3
from moto import mock_dynamodb2
from handler import create_todo, get_todo, update_todo, delete_todo
import os

@pytest.fixture
def todos_table():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION"))
        table = dynamodb.create_table(
            TableName='todo-api-todos',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        yield table

def test_create_todo(todos_table):
    event = {'body': json.dumps({'title': 'New Todo', 'metadata': {}})}
    result = create_todo(event, None)
    body = json.loads(result['body'])
    assert result['statusCode'] == 201
    assert body['title'] == 'New Todo'
    assert body['completed'] is False

def test_get_todo(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = get_todo(event, None)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Sample Todo'

def test_update_todo(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}, 'body': json.dumps({'title': 'Updated Todo', 'completed': True, 'metadata': {}})}
    result = update_todo(event, None)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Updated Todo'

def test_delete_todo_completed(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': True, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    assert result['statusCode'] == 204

def test_delete_todo_not_completed(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    body = json.loads(result['body'])
    assert result['statusCode'] == 400
    assert body['error'] == 'Todo must be completed to be deleted'
