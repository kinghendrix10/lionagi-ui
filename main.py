# main.py
import streamlit as st
from ui.streamlit_app import main as run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()

# agents/agent.py
from lionagi import System, Instruction, GraphExecutor, InstructionMapEngine, BaseAgent
from utils.parsers import master_parser, assistant_parser

class Agent:
    def __init__(self, name, role, instructions, parent=None, is_lead=False):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.parent = parent
        self.children = []
        self.system = System(system=role)
        self.instruction = Instruction(instructions)
        self.graph = GraphExecutor()
        self.graph.add_node(self.system)
        self.graph.add_node(self.instruction)
        self.graph.add_edge(self.system, self.instruction)
        self.executable = InstructionMapEngine()
        self.is_lead = is_lead
        self.parser = master_parser if is_lead else assistant_parser

    def add_child(self, child):
        self.children.append(child)
        self.graph.add_node(child.system)
        self.graph.add_edge(self.instruction, child.system)

    def remove_child(self, child):
        self.children.remove(child)
        self.graph.remove_node(child.system)

    def to_base_agent(self):
        return BaseAgent(
            structure=self.graph,
            executable=self.executable,
            output_parser=self.parser
        )
