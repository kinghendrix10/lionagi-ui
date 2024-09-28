# agents/agent_network.py
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from utils.report_generator import markdown_to_pdf
from io import BytesIO


class AgentNetwork:
    def __init__(self):
        self.agents = {}
        self.root = None
        self.analysis_process = nx.DiGraph()

    def add_agent(self, agent):
        self.agents[agent.name] = agent
        if agent.parent is None:
            self.root = agent
        else:
            parent_agent = self.agents[agent.parent]
            parent_agent.add_child(agent)
            self.analysis_process.add_edge(parent_agent.name, agent.name)

    def remove_agent(self, agent_name):
        agent = self.agents[agent_name]
        if agent.parent:
            parent = self.agents[agent.parent]
            parent.remove_child(agent)
            self.analysis_process.remove_edge(parent.name, agent.name)
        for child in agent.children:
            child.parent = None
            self.analysis_process.remove_edge(agent.name, child.name)
        del self.agents[agent_name]

    def execute(self):
        if not self.root:
            return "No root agent defined"
        
        result = []
        
        for node in nx.topological_sort(self.analysis_process):
            agent = self.agents[node]
            result.append(agent.base_agent.execute())
        
        return result

    def generate_report(self, project_name):
        if not self.root:
            return None
        
        report_buffer = BytesIO()
        
        report_content = []
        
        for node in nx.topological_sort(self.analysis_process):
            agent = self.agents[node]
            report_content.append(agent.display())
        
        df = pd.DataFrame(report_content).T
        markdown_to_pdf(df, report_buffer, project_name)
        
        report_buffer.seek(0)
        
        return report_buffer

    def visualize_network(self):
        G = nx.DiGraph()
        
        for agent in self.agents.values():
            G.add_node(agent.name)
            if agent.parent:
                G.add_edge(agent.parent, agent.name)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=3000, font_size=10, font_weight='bold')
        
        plt.title("Agent Network Structure")
        
        st.pyplot(plt)