# agents/agent.py
from lionagi.core.message import System, Instruction
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.agent.base_agent import BaseAgent
from utils.parsers import master_parser, assistant_parser

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
        self.graph.add_node(child.system)
        self.graph.add_edge(self.instruction, child.system)

    def remove_child(self, child):
        self.children.remove(child)
        self.graph.remove_node(child.system)

    def display(self):
        return f"Agent: {self.name}, Role: {self.system}, Instructions: {self.instruction}"