# utils/parsers.py
def master_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        output.append(branch.to_df())
    return output

def assistant_parser(agent):
    output = []
    for branch in agent.executable.branches.values():
        for msg in branch.to_chat_messages():
            if msg["role"] == "assistant":
                output.append(msg["content"])
    return output
