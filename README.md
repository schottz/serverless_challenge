# Serverless Home Assignment

Serverless Home Assignment aimed to show my serverless knowledge.

## Endpoints
 
- POST /todos body: {"title": "New task", "completed": 0}  Create a new todo item

- GET /todos/{id}: Retrieve a todo item by id
- PUT /todos/{id} body: {"completed": 1} Update a todo item by id
- DELETE /todos/{id}: Delete a completed todo item by id if it is completed.

## Setup

1. Install Serverless Framework:
   ```sh
   npm install -g serverless

2. Deploy:
   ```sh
   serverless deploy

## Running Locally

1. Deploy:
   ```sh
   serverless offline

## Testing

```sh
   pip install -r requirements.txt
   pytest test_handler.py