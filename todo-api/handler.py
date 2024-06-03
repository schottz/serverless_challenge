import json
import uuid
import boto3
from botocore.exceptions import ClientError
from jsonschema import validate, ValidationError
import os

TABLE_NAME = 'todo-list'

if os.getenv('IS_OFFLINE'):
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
else:
    dynamodb = boto3.resource('dynamodb', region_name='sa-east-1')

create_schema = {
    "properties": {
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
        "metadata": {"type": "object"}
    },
    "required": ["title"]
}

update_schema = {
    "properties": {
        "title": {"type": "string"},
        "completed": {"type": "boolean"},
        "metadata": {"type": "object"}
    },
    "required": ["completed"]
}

def validate_request_body(body, request):
    try:
        validate(instance=body, schema=create_schema if request == "create" else update_schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def create_todo(event, context):
    is_valid, error_message = validate_request_body(json.loads(event['body']), "create")
    if not is_valid:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }
    
    data = json.loads(event['body'])
    todo_id = str(uuid.uuid4())
    table = dynamodb.Table(TABLE_NAME)

    item = {
        'id': todo_id,
        'title': data['title'],
        'completed': False,
        'metadata': data.get('metadata', {})
    }

    table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps(item)
    }

def get_todo(event, context):
    todo_id = event['pathParameters']['id']
    table = dynamodb.Table(TABLE_NAME)

    try:
        response = table.get_item(Key={'id': todo_id})
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Todo not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def update_todo(event, context):
    is_valid, error_message = validate_request_body(json.loads(event['body']), "update")
    if not is_valid:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }
    
    todo_id = event['pathParameters']['id']
    data = json.loads(event['body'])
    table = dynamodb.Table(TABLE_NAME)

    update_expression = "SET "
    expression_attribute_values = {}

    if 'title' in data:
        update_expression += "title = :title, "
        expression_attribute_values[':title'] = data['title']
    if 'completed' in data:
        update_expression += "completed = :completed, "
        expression_attribute_values[':completed'] = bool(data['completed'])
    if 'metadata' in data:
        update_expression += "metadata = :metadata, "
        expression_attribute_values[':metadata'] = data['metadata']

    update_expression = update_expression.rstrip(', ')

    try:
        response = table.update_item(
            Key={'id': todo_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def delete_todo(event, context):
    todo_id = event['pathParameters']['id']
    table = dynamodb.Table(TABLE_NAME)

    try:
        response = table.delete_item(
            Key={'id': todo_id},
            ConditionExpression='completed = :completed',
            ExpressionAttributeValues={':completed': True}
        )
        return {
            'statusCode': 204,
            'body': ''
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Todo must be completed to be deleted'})
            }
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
