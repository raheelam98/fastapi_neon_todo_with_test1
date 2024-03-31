from fastapi.testclient import TestClient
from fastapi_neon2.main import app

from fastapi_neon2.model import test_create_db_tables,test_engine, get_session, Todo

import pytest
from sqlmodel import Session

#### ==================== fixture ==================== #####

# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/?h=test

# create session for test
@pytest.fixture(name="session")
def session_fixture():
    test_create_db_tables()
    with Session(test_engine) as session:   
        yield session

# Create the new fixture named "client"
@pytest.fixture(name="client") 
def client_fixture(session : Session):  # This client fixture, in turn, also requires the session fixture.

    # Define the new function that will be the new dependency override.
    def get_session_override():
        return session 
    
    # Here's where we create the custom session object for this test in a with block.
    # It uses the new custom engine we created, so anything that uses this session will be using the testing database.
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    
    # we can restore the application back to normal, by removing all the values in this dictionary app.dependency_overrides. 
    app.dependency_overrides.clear()
   
#### ==================== read main file ==================== #####
    
# function to read main file
def test_read_main():
    #create TestClind for the fastapi app
    clinet = TestClient(app=app)
    response = clinet.get('/')
    assert response.status_code == 200
    assert response.json() == {"Fast API": "Todo"} 

#### ==================== Get Data From Test Database ==================== #####

# get todo from test-db
def test_get_todo(client : TestClient):
    response = client.get('/get_todos')
    assert response.status_code == 200    
   
#### ==================== Add Data Into Test Database ==================== #####

def test_write_in_test_db(client : TestClient):
    todo_content = "Computer Science"
    response = client.post("/todos/",  json={"todo_name": todo_content})

    data = response.json()

    assert response.status_code == 200
    assert data["todo_name"] == todo_content

#### ====================  ==================== #####    
    
#### ====================  ==================== #####        


# Error :- assert 404 == 200,  E +  where 404 = <Response [404 Not Found]>.status_code
# Error :- assert 422 == 200,  E +  where 422 = <Response [422 Unprocessable Entity]>.status_code