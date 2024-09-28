# agents/agent_definitions.py
from agents.agent import Agent
from utils.parsers import master_parser, assistant_parser

def create_master_agent(name, role, instructions):
    return Agent(
        name=name,
        role=role,
        instructions=instructions,
        is_lead=True
    )

def create_assistant_agent(name, role, instructions, parent=None):
    return Agent(
        name=name,
        role=role,
        instructions=instructions,
        parent=parent,
        is_lead=False
    )

sample_master_agent = {
    "name": "BusinessIdea",
    "role": "An experienced business analyst with a keen eye for market opportunities and potential pitfalls",
    "instructions": """As an expert business analyst, evaluate the given business idea. 
    Assess its viability, potential, and uniqueness in the market. 
    Identify key strengths, weaknesses, opportunities, and threats. 
    Provide an objective analysis of the idea, potential for success and any areas that need improvement."""
}

sample_assistant_agent = {
    "name": "MarketResearch",
    "role": "A data-driven market research specialist with extensive knowledge of various industries and market trends.",
    "instructions": """As a seasoned market research specialist, conduct a comprehensive market analysis for the given business idea. 
    Determine the Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM). 
    Identify key market trends, growth potential, and competitive landscape. 
    Provide data-backed insights to support your analysis."""
}
