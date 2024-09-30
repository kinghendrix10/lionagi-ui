# agents/agent.py
from lionagi.core.message import System, Instruction
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.agent.base_agent import BaseAgent
from utils.parsers import master_parser, assistant_parser
import networkx as nx 

import os
from dotenv import load_dotenv

load_dotenv()

os.environ['CEREBRAS_API_KEY'] = os.getenv("CEREBRAS_API_KEY")

from lionagi.integrations.config import cerebras_schema

cerebras_schema["API_key_schema"] = os.environ["CEREBRAS_API_KEY"]

class Agent:
    def __init__(self, name, role, instructions, parent=None, is_lead=False):
        self.name = name
        self.system = System(system=role)
        self.instruction = Instruction(instructions)
        self.parent = parent
        self.children = []
        self.graph = GraphExecutor()
        self.graph.add_node(self.system)
        self.graph.add_node(self.instruction)
        self.graph.add_edge(self.system, self.instruction)
        self.executable = InstructionMapEngine()
        self.is_lead = is_lead
        self.base_agent = BaseAgent(
            structure=self.graph,
            executable=self.executable,
            output_parser=master_parser if is_lead else assistant_parser
        )

    def add_child(self, child):
        self.children.append(child)
        # Merge the child's graph into the parent's graph
        self.merge_graphs(child.graph)
        # Add an edge from this agent's instruction to the child's system node
        self.graph.add_edge(self.instruction, child.system)

    def merge_graphs(self, other_graph):
        # Merge nodes
        for node_id, node in other_graph.internal_nodes.items():
            if node_id not in self.graph.internal_nodes:
                self.graph.internal_nodes[node_id] = node
        # Merge edges
        for edge_id, edge in other_graph.internal_edges.items():
            if edge_id not in self.graph.internal_edges:
                self.graph.internal_edges[edge_id] = edge

    def remove_child(self, child):
        self.children.remove(child)
        self.graph.remove_node(child.system)

    def report(self):
        # return f"Agent: {self.name}, Role: {self.system}, Instructions: {self.instruction}"
        return self.base_agent.executable