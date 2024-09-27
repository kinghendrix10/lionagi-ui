// static/js/scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    // Agent management
    const agentForm = document.getElementById('agent-form');
    const agentList = document.getElementById('agent-list');

    if (agentForm) {
        agentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(agentForm);
            const agentData = Object.fromEntries(formData.entries());

            fetch('/agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(agentData),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                loadAgents();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    function loadAgents() {
        fetch('/agents')
        .then(response => response.json())
        .then(agents => {
            agentList.innerHTML = '';
            agents.forEach(agent => {
                const li = document.createElement('li');
                li.textContent = `${agent.name} (${agent.role})`;
                li.addEventListener('click', () => loadAgentDetails(agent.id));
                agentList.appendChild(li);
            });
        });
    }

    function loadAgentDetails(agentId) {
        fetch(`/agents/${agentId}`)
        .then(response => response.json())
        .then(agent => {
            document.getElementById('agent-name').value = agent.name;
            document.getElementById('agent-role').value = agent.role;
            document.getElementById('agent-instructions').value = agent.instructions;
            document.getElementById('agent-reporting-to').value = agent.reporting_to || '';
        });
    }

    // Tool management
    const toolForm = document.getElementById('tool-form');
    const toolList = document.getElementById('tool-list');

    if (toolForm) {
        toolForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(toolForm);
            const toolData = Object.fromEntries(formData.entries());

            fetch('/tools', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(toolData),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                loadTools();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    function loadTools() {
        fetch('/tools')
        .then(response => response.json())
        .then(tools => {
            toolList.innerHTML = '';
            tools.forEach(tool => {
                const li = document.createElement('li');
                li.textContent = `${tool.name}: ${tool.description}`;
                toolList.appendChild(li);
            });
        });
    }

    // API Service management
    const apiForm = document.getElementById('api-form');
    const apiList = document.getElementById('api-list');

    if (apiForm) {
        apiForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(apiForm);
            const apiData = Object.fromEntries(formData.entries());

            fetch('/api_services', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(apiData),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                loadAPIServices();
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    function loadAPIServices() {
        fetch('/api_services')
        .then(response => response.json())
        .then(services => {
            apiList.innerHTML = '';
            services.forEach(service => {
                const li = document.createElement('li');
                li.textContent = service.name;
                apiList.appendChild(li);
            });
        });
    }

    // Execute agents
    const executeButton = document.getElementById('execute-agents');
    if (executeButton) {
        executeButton.addEventListener('click', function() {
            const projectName = document.getElementById('project-name').value || 'Business Idea';
            fetch('/execute_agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({project_name: projectName}),
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `${projectName}_report.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
    }

    const updateDatabaseButton = document.getElementById('update-database');
    if (updateDatabaseButton) {
        updateDatabaseButton.addEventListener('click', function() {
            fetch('/update_database', {
                method: 'POST',
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                alert('Database updated successfully');
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Failed to update database');
            });
        });
    }
    // Load initial data
    if (agentList) loadAgents();
    if (toolList) loadTools();
    if (apiList) loadAPIServices();
});

