# ui/streamlit_app.py
import streamlit as st
from agents.agent_network import AgentNetwork
from agents.agent_definitions import create_master_agent, create_assistant_agent, sample_master_agent, sample_assistant_agent

def main():
    st.title("Dynamic Agent Network Builder")

    network = AgentNetwork()

    st.header("Create Master Agent")
    master_name = st.text_input("Master Agent Name", value=sample_master_agent["name"])
    master_role = st.text_area("Master Agent Role", value=sample_master_agent["role"])
    master_instructions = st.text_area("Master Agent Instructions", value=sample_master_agent["instructions"])

    if st.button("Create Master Agent"):
        master_agent = create_master_agent(master_name, master_role, master_instructions)
        network.add_agent(master_agent)
        st.success(f"Master Agent '{master_name}' created successfully!")

    st.header("Create Assistant Agents")
    num_assistants = st.number_input("Number of Assistant Agents", min_value=1, value=1)

    for i in range(num_assistants):
        st.subheader(f"Assistant Agent {i+1}")
        asst_name = st.text_input(f"Name for Assistant {i+1}", value=f"{sample_assistant_agent['name']}_{i+1}")
        asst_role = st.text_area(f"Role for Assistant {i+1}", value=sample_assistant_agent["role"])
        asst_instructions = st.text_area(f"Instructions for Assistant {i+1}", value=sample_assistant_agent["instructions"])
        asst_parent = st.selectbox(f"Parent for Assistant {i+1}", options=[agent.name for agent in network.agents.values()])

        if st.button(f"Create Assistant Agent {i+1}"):
            asst_agent = create_assistant_agent(asst_name, asst_role, asst_instructions, asst_parent)
            network.add_agent(asst_agent)
            st.success(f"Assistant Agent '{asst_name}' created successfully!")

    if st.button("Execute Agent Network"):
        if network.root:
            with st.spinner("Executing agent network..."):
                result = network.execute()
                st.success("Execution complete!")
                st.write(result)
        else:
            st.warning("Please create a master agent before executing the network.")

    if st.button("Visualize Agent Network"):
        network.visualize_network()

if __name__ == "__main__":
    main()

# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
