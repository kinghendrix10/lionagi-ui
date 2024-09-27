# app/routes.py

from flask import Blueprint, request, jsonify
from .models import db, Project, Agent, Analysis, APIService
from .utils import create_agent, build_agent_graph, execute_agents, generate_report

main = Blueprint('main', __name__)

@main.route('/projects', methods=['GET', 'POST'])
def manage_projects():
    if request.method == 'POST':
        data = request.json
        new_project = Project(name=data['name'], description=data['description'])
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Project created successfully", "id": new_project.id}), 201
    
    projects = Project.query.all()
    return jsonify([{"id": p.id, "name": p.name, "description": p.description} for p in projects])

@main.route('/projects/<int:project_id>', methods=['GET', 'PUT', 'DELETE'])
def project_operations(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'GET':
        return jsonify({
            "id": project.id,
            "name": project.name,
            "description": project.description
        })
    
    elif request.method == 'PUT':
        data = request.json
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        db.session.commit()
        return jsonify({"message": "Project updated successfully"})
    
    elif request.method == 'DELETE':
        db.session.delete(project)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"})

@main.route('/projects/<int:project_id>/agents', methods=['GET', 'POST'])
def manage_agents(project_id):
    if request.method == 'POST':
        data = request.json
        new_agent = Agent(
            name=data['name'],
            role=data['role'],
            instructions=data['instructions'],
            reporting_to=data.get('reporting_to'),
            project_id=project_id
        )
        db.session.add(new_agent)
        db.session.commit()
        return jsonify({"message": "Agent created successfully", "id": new_agent.id}), 201
    
    agents = Agent.query.filter_by(project_id=project_id).all()
    return jsonify([{
        "id": a.id,
        "name": a.name,
        "role": a.role,
        "reporting_to": a.reporting_to
    } for a in agents])

@main.route('/agents/<int:agent_id>', methods=['GET', 'PUT', 'DELETE'])
def agent_operations(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    
    if request.method == 'GET':
        return jsonify({
            "id": agent.id,
            "name": agent.name,
            "role": agent.role,
            "instructions": agent.instructions,
            "reporting_to": agent.reporting_to
        })
    
    elif request.method == 'PUT':
        data = request.json
        agent.name = data.get('name', agent.name)
        agent.role = data.get('role', agent.role)
        agent.instructions = data.get('instructions', agent.instructions)
        agent.reporting_to = data.get('reporting_to', agent.reporting_to)
        db.session.commit()
        return jsonify({"message": "Agent updated successfully"})
    
    elif request.method == 'DELETE':
        db.session.delete(agent)
        db.session.commit()
        return jsonify({"message": "Agent deleted successfully"})

@main.route('/projects/<int:project_id>/execute', methods=['POST'])
def execute_analysis(project_id):
    project = Project.query.get_or_404(project_id)
    agents = Agent.query.filter_by(project_id=project_id).all()
    
    graph, agent_nodes = build_agent_graph(agents)
    results = execute_agents(agent_nodes)
    
    for agent_id, result in results.items():
        analysis = Analysis(project_id=project_id, agent_id=agent_id, results=result)
        db.session.add(analysis)
    
    db.session.commit()
    
    report = generate_report(results, project.name)
    return jsonify({"message": "Analysis completed", "report": report})

@main.route('/projects/<int:project_id>/report', methods=['GET'])
def get_report(project_id):
    analyses = Analysis.query.filter_by(project_id=project_id).order_by(Analysis.created_at.desc()).all()
    if not analyses:
        return jsonify({"error": "No analysis found for this project"}), 404
    
    results = {a.agent_id: a.results for a in analyses}
    report = generate_report(results, Project.query.get(project_id).name)
    return jsonify({"report": report})

@main.route('/api_services', methods=['GET', 'POST'])
def manage_api_services():
    if request.method == 'POST':
        data = request.json
        new_service = APIService(name=data['name'], key=data['key'])
        db.session.add(new_service)
        db.session.commit()
        return jsonify({"message": "API service added successfully", "id": new_service.id}), 201
    
    services = APIService.query.all()
    return jsonify([{"id": s.id, "name": s.name} for s in services])
