# agents/agent_network.py
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

class AgentNetwork:
    def __init__(self):
        self.agents = {}
        self.root = None

    def add_agent(self, agent):
        self.agents[agent.name] = agent
        if agent.parent is None:
            self.root = agent
        else:
            parent = self.agents[agent.parent]
            parent.add_child(agent)

    def remove_agent(self, agent_name):
        agent = self.agents[agent_name]
        if agent.parent:
            parent = self.agents[agent.parent]
            parent.remove_child(agent)
        for child in agent.children:
            child.parent = None
        del self.agents[agent_name]

    def update_agent(self, agent_name, role, instructions, parent):
        agent = self.agents[agent_name]
        agent.role = role
        agent.instructions = instructions
        if agent.parent != parent:
            if agent.parent:
                old_parent = self.agents[agent.parent]
                old_parent.remove_child(agent)
            if parent:
                new_parent = self.agents[parent]
                new_parent.add_child(agent)
            agent.parent = parent

    def execute(self):
        if self.root:
            return self.root.to_base_agent().execute()
        else:
            return "No root agent defined"

    def generate_report(self, project_name, output_filename):
        if self.root:
            ex = self.root.to_base_agent().executable
            messages = pd.DataFrame(ex.branches.values())
            output = list(pd.DataFrame(messages[5].to_list())[1])
            df = pd.DataFrame(output).T
            markdown_to_pdf(df, output_filename, project_name)
        else:
            print("No root agent defined, cannot generate report.")

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
        
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.title("Agent Network Structure")
        st.pyplot(plt)
