# app/models.py

from . import db
from sqlalchemy.dialects.postgresql import JSON

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    reporting_to = db.Column(db.Integer, db.ForeignKey('agent.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    results = db.Column(JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class APIService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(200), nullable=False)
