# /app/app.py

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask import jsonify
import subprocess
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
migrate = Migrate(app, db)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    reporting_to = db.Column(db.String(100))
    agent_type = db.Column(db.String(100))

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
            reporting_to=request.json.get('reporting_to'),
            agent_type=request.json.get('agent_type')
        )
        db.session.add(new_agent)
        db.session.commit()
        return jsonify({"message": "Agent created successfully"}), 201
    
    agents = Agent.query.all()
    return jsonify([{
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "reporting_to": agent.reporting_to,
        "agent_type": agent.agent_type
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
            "reporting_to": agent.reporting_to,
            "agent_type": agent.agent_type
        })
    
    elif request.method == 'PUT':
        agent.name = request.json.get('name', agent.name)
        agent.role = request.json.get('role', agent.role)
        agent.instructions = request.json.get('instructions', agent.instructions)
        agent.reporting_to = request.json.get('reporting_to', agent.reporting_to)
        agent.agent_type = request.json.get('agent_type', agent.agent_type)
        db.session.commit()
        return jsonify({"message": "Agent updated successfully"})
    
    elif request.method == 'DELETE':
        db.session.delete(agent)
        db.session.commit()
        return jsonify({"message": "Agent deleted successfully"})

def master_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        output.append(branch.to_df())
    return output

def assistant_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        for msg in branch.to_chat_messages():
            if msg["role"] == "assistant":
                output.append(msg["content"])
    return output

def create_agent(agent_data):
    system = System(system=agent_data.role)
    instruction = Instruction(agent_data.instructions)
    graph = GraphExecutor()
    graph.add_node(system)
    graph.add_node(instruction)
    graph.add_edge(system, instruction)
    exe = InstructionMapEngine()
    return BaseAgent(
        structure=graph,
        executable=exe,
        output_parser=assistant_parser if agent_data.agent_type != 'BusinessIdea' else master_parser
    )

def build_agent_graph(agents):
    graph = GraphExecutor()
    agent_nodes = {}
    for agent in agents:
        agent_node = create_agent(agent)
        agent_nodes[agent.name] = agent_node
        graph.add_node(agent_node)
    
    for agent in agents:
        if agent.reporting_to and agent.reporting_to in agent_nodes:
            graph.add_edge(agent_nodes[agent.reporting_to], agent_nodes[agent.name])
    
    return graph, agent_nodes

@app.route('/execute_agents', methods=['POST'])
async def execute_agents():
    project_name = request.json.get('project_name', 'Business Idea')
    
    agents = Agent.query.all()
    graph, agent_nodes = build_agent_graph(agents)
    
    results = {}
    for agent_name, agent_node in agent_nodes.items():
        if agent_name not in results:
            result = await agent_node.execute()
            results[agent_name] = result
    
    report_file = generate_report(results, project_name)
    return send_file(report_file, as_attachment=True)

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

@app.route('/update_database', methods=['POST'])
def update_database():
    try:
        # Run database migrations
        with app.app_context():
            upgrade()
        
        # Run the Flask-Migrate commands
        subprocess.run(["flask", "db", "migrate"], check=True)
        subprocess.run(["flask", "db", "upgrade"], check=True)
        
        return jsonify({"message": "Database updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_api_keys()
    socketio.run(app, debug=True)
