# test_app.py

import pytest
from app import create_app, db
from app.models import Project, Agent, Analysis, APIService

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    db.drop_all()

def test_create_project(client):
    response = client.post('/projects', json={
        'name': 'Test Project',
        'description': 'A test project'
    })
    assert response.status_code == 201
    assert b'Test Project' in response.data

def test_create_agent(client):
    # First, create a project
    client.post('/projects', json={
        'name': 'Test Project',
        'description': 'A test project'
    })
    
    response = client.post('/projects/1/agents', json={
        'name': 'Test Agent',
        'role': 'Analyst',
        'instructions': 'Analyze the data'
    })
    assert response.status_code == 201
    assert b'Test Agent' in response.data

def test_execute_analysis(client):
    # Create a project and an agent
    client.post('/projects', json={
        'name': 'Test Project',
        'description': 'A test project'
    })
    client.post('/projects/1/agents', json={
        'name': 'Test Agent',
        'role': 'Analyst',
        'instructions': 'Analyze the data'
    })
    
    response = client.post('/projects/1/execute')
    assert response.status_code == 200
    assert b'Analysis completed' in response.data

def test_get_report(client):
    # Create a project, agent, and execute analysis
    client.post('/projects', json={
        'name': 'Test Project',
        'description': 'A test project'
    })
    client.post('/projects/1/agents', json={
        'name': 'Test Agent',
        'role': 'Analyst',
        'instructions': 'Analyze the data'
    })
    client.post('/projects/1/execute')
    
    response = client.get('/projects/1/report')
    assert response.status_code == 200
    assert b'Test Project' in response.data
    assert b'Test Agent' in response.data
