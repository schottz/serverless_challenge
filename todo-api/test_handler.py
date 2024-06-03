import json
import pytest
import boto3
from moto import mock_dynamodb2
from handler import create_todo, get_todo, update_todo, delete_todo
import os

@pytest.fixture
def todos_table():
    table_name = "todo-list"
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION", "us-east-1"))
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        # Ensure the table is created before proceeding
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        yield table

def test_create_todo(todos_table):
    event = {'body': json.dumps({'title': 'New Todo', 'metadata': {}})}
    result = create_todo(event, None)
    print("Create Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 201
    assert body['title'] == 'New Todo'
    assert body['completed'] is False

def test_get_todo(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = get_todo(event, None)
    print("Get Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Sample Todo'

def test_update_todo(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}, 'body': json.dumps({'title': 'Updated Todo', 'completed': True, 'metadata': {}})}
    result = update_todo(event, None)
    print("Update Todo Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 200
    assert body['title'] == 'Updated Todo'

def test_delete_todo_completed(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': True, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    print("Delete Todo Completed Result:", result)
    assert result['statusCode'] == 204

def test_delete_todo_not_completed(todos_table):
    todos_table.put_item(Item={'id': '123', 'title': 'Sample Todo', 'completed': False, 'metadata': {}})
    event = {'pathParameters': {'id': '123'}}
    result = delete_todo(event, None)
    print("Delete Todo Not Completed Result:", result)
    body = json.loads(result['body'])
    assert result['statusCode'] == 400
    assert body['error'] == 'Todo must be completed to be deleted'
