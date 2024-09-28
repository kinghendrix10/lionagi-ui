# ui/streamlit_app.py
import asyncio
import streamlit as st
from agents.agent_network import AgentNetwork
from agents.agent import Agent
import nest_asyncio

nest_asyncio.apply()

def main():
    st.title("Agent Network Builder")

    network = AgentNetwork()

    st.header("Create Master Agent")
    master_name = st.text_input("Master Agent Name", value="BusinessIdea")
    master_role = st.text_area("Master Agent Role", value="An experienced business analyst with a keen eye for market opportunities and potential pitfalls")
    master_instructions = st.text_area("Master Agent Instructions", value="As an expert business analyst, evaluate the given business idea. Assess its viability, potential, and uniqueness in the market. Identify key strengths, weaknesses, opportunities, and threats. Provide an objective analysis of the idea, potential for success and any areas that need improvement.")

    master_agent = Agent(master_name, master_role, master_instructions, is_lead=True)
    print(master_agent)
    network.add_agent(master_agent)

    st.header("Create Assistant Agents")
    num_assistants = st.number_input("Number of Assistant Agents", min_value=1, value=1)

    for i in range(num_assistants):
        st.subheader(f"Assistant Agent {i+1}")
        asst_name = st.text_input(f"Name for Assistant {i+1}", value=f"AssistantAgent_{i+1}")
        asst_role = st.text_area(f"Role for Assistant {i+1}", value="A specialized assistant agent")
        asst_instructions = st.text_area(f"Instructions for Assistant {i+1}", value="Perform specialized tasks as instructed by the parent agent.")
        asst_parent = st.selectbox(f"Parent for Assistant {i+1}", options=[agent.name for agent in network.agents.values()])

        asst_agent = Agent(asst_name, asst_role, asst_instructions, parent=asst_parent)
        network.add_agent(asst_agent)

    project_name = st.text_input("Enter project name for the report")
    if project_name and st.button("Execute Agent Network and Generate Report"):
        with st.spinner("Executing agent network..."):
            # Run the coroutine properly
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(network.execute())
            st.success("Execution complete!")
            st.write(result)

            report_buffer = network.generate_report(project_name)
            if report_buffer:
                st.download_button(
                    label="Download Report",
                    data=report_buffer,
                    file_name=f"{project_name}_report.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("Failed to generate report. Please ensure the agent network is properly set up.")

    if st.button("Visualize Agent Network"):
        network.visualize_network()

if __name__ == "__main__":
    main()
