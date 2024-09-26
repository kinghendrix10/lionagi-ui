# /app/app.py

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import asyncio
import os
from dotenv import load_dotenv
from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.message import System, Instruction
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app)
db = SQLAlchemy(app)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    reporting_to = db.Column(db.String(100))

class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class APIService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/configure')
def configure():
    return render_template('configure.html')

@app.route('/agents', methods=['GET', 'POST'])
def manage_agents():
    if request.method == 'POST':
        new_agent = Agent(
            name=request.json['name'],
            role=request.json['role'],
            instructions=request.json['instructions'],
            reporting_to=request.json.get('reporting_to')
        )
        db.session.add(new_agent)
        db.session.commit()
        return jsonify({"message": "Agent created successfully"}), 201
    
    agents = Agent.query.all()
    return jsonify([{
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "reporting_to": agent.reporting_to
    } for agent in agents])

@app.route('/agents/<int:agent_id>', methods=['GET', 'PUT', 'DELETE'])
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
        agent.name = request.json.get('name', agent.name)
        agent.role = request.json.get('role', agent.role)
        agent.instructions = request.json.get('instructions', agent.instructions)
        agent.reporting_to = request.json.get('reporting_to', agent.reporting_to)
        db.session.commit()
        return jsonify({"message": "Agent updated successfully"})
    
    elif request.method == 'DELETE':
        db.session.delete(agent)
        db.session.commit()
        return jsonify({"message": "Agent deleted successfully"})

@app.route('/execute_agents', methods=['POST'])
def execute_agents():
    project_name = request.json.get('project_name', 'Business Idea')
    
    agents = Agent.query.all()
    graph_executor = GraphExecutor()
    base_agents = {}

    for agent in agents:
        agent_node = System(system=agent.role)
        agent_inst = Instruction(agent.instructions)
        graph_executor.add_node(agent_node)
        graph_executor.add_node(agent_inst)
        graph_executor.add_edge(agent_node, agent_inst)
        
        agent_exe = InstructionMapEngine()
        base_agent = BaseAgent(
            structure=graph_executor,
            executable=agent_exe,
            output_parser=assistant_parser
        )
        base_agents[agent.name] = base_agent

    results = {}
    for agent in agents:
        if agent.name not in results:
            result = asyncio.run(base_agents[agent.name].execute())
            results[agent.name] = result

    report_file = generate_report(results, project_name)
    return send_file(report_file, as_attachment=True)

def assistant_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        for msg in branch.to_chat_messages():
            if msg["role"] == "assistant":
                output.append(msg["content"])
    return output

def generate_report(results, project_name):
    doc = SimpleDocTemplate(f"{project_name}_report.pdf", pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    content = []
    content.append(Paragraph(project_name, styles['Title']))
    content.append(Spacer(1, 12))

    for agent_name, result in results.items():
        content.append(Paragraph(f"Report from {agent_name}:", styles['Heading2']))
        content.append(Spacer(1, 6))
        content.append(Paragraph(str(result), styles['Justify']))
        content.append(Spacer(1, 12))

    doc.build(content)
    return f"{project_name}_report.pdf"

def load_api_keys():
    api_services = APIService.query.all()
    for service in api_services:
        if service.name.lower() == 'openai':
            os.environ["OPENAI_API_KEY"] = service.key

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_api_keys()
    socketio.run(app, debug=True)
