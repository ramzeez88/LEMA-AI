
class _RoutingAgent:
    def __init__(self,llm):
        self.llm = llm

    def select_agent(self, user_input):
        routing_agent_response = self.llm.create_chat_completion(
            
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant.You are responsible for selecting appropriate agent based on the input you recieve. You MUST only respond with the agent's name. Agents to choose from are 1.'Function_call' which can perform actions and execute commands or 2.'Chat_agent' for anything else, including telling jokes. If you think the user input is not valid, respond with 'Chat_agent'."},
                {"role": "user", "content": "What is the capital of France?"},
                {"role": "assistant", "content": "Chat_agent"},
                {"role": "user", "content": "i heard you can do lots of things !"},
                {"role": "assistant", "content": "Chat_agent"},
                {"role": "user", "content": "Tell me a joke."},
                {"role": "assistant", "content": "Chat_agent"},
                {"role": "user", "content": " you can exit now"},
                {"role": "assistant", "content": "function_call"},
                {"role": "user", "content": "can you save it to a notepad ?"},
                {"role": "assistant", "content": "function_call"},
                {"role": "user", "content": "what is 34+45/4 ?"},
                {"role": "assistant", "content": "Chat_agent"},
                {"role": "user", "content": "Open a web browser."},
                {"role": "assistant", "content": "Function_call"},
                {"role": "user", "content": "would you mind to run a calculator?"},
                {"role": "assistant", "content": "Function_call"},
                {"role": "user", "content": user_input}
            ],
            temperature=0,
            stream=False,
            max_tokens= 20
        )

        selected_agent = routing_agent_response['choices'][0]['message']['content'].strip().lower()
        print(selected_agent)
       
        return selected_agent
