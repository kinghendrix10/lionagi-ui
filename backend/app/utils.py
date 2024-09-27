# app/utils.py

from lionagi.core.agent.base_agent import BaseAgent
from lionagi.core.executor.graph_executor import GraphExecutor
from lionagi.core.engine.instruction_map_engine import InstructionMapEngine
from lionagi.core.message import System, Instruction

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
        output_parser=lambda x: [msg["content"] for branch in x.executable.branches.values() for msg in branch.to_chat_messages() if msg["role"] == "assistant"]
    )

def build_agent_graph(agents):
    graph = GraphExecutor()
    agent_nodes = {}
    for agent in agents:
        agent_node = create_agent(agent)
        agent_nodes[agent.id] = agent_node
        graph.add_node(agent_node)
    
    for agent in agents:
        if agent.reporting_to and agent.reporting_to in agent_nodes:
            graph.add_edge(agent_nodes[agent.reporting_to], agent_nodes[agent.id])
    
    return graph, agent_nodes

async def execute_agents(agent_nodes):
    results = {}
    for agent_id, agent_node in agent_nodes.items():
        result = await agent_node.execute()
        results[agent_id] = result
    return results

def generate_report(results, project_name):
    report = f"Analysis Report for {project_name}\n\n"
    for agent_id, result in results.items():
        report += f"Agent {agent_id} Report:\n"
        report += "\n".join(result)
        report += "\n\n"
    return report
