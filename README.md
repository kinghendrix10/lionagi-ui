# lionagi-ui

## Project Description

LionAGI-UI is a user interface for building and managing agent for reasearch purposes. It allows users to create master and assistant agents, define their roles and instructions, and visualize the agent network structure using the LionAGI framework. The project aims to provide a flexible and intuitive interface for managing complex agent networks.

## Features

- Create and manage master and assistant agents
- Define roles and instructions for each agent
- Visualize the agent network structure
- Generate reports based on agent network execution

## Configuration

The application uses environment variables to manage configuration settings. Create a `.env` file in the root directory of the project and add the following environment variables:

```
CEREBRAS_API_KEY=your_cerebras_api_key
```

## Installation

To install the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/kinghendrix10/lionagi-ui.git
   cd lionagi-ui
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install git+https://github.com/kinghendrix10/lionagi@main
   ```

## Usage

To run the Streamlit app, use the following command:
```bash
streamlit run main.py
```

This will start the Streamlit app, allowing you to create and manage agent networks through the user interface.

## Main Files and Directories

- `agents/agent_definitions.py`: Contains functions to create master and assistant agents with predefined roles and instructions.
- `agents/agent_network.py`: Defines the `AgentNetwork` class, which manages the agent network structure, execution, and report generation.
- `ui/streamlit_app.py`: Contains the Streamlit app code, providing the user interface for creating and managing agent networks.
