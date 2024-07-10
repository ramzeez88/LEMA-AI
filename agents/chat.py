from agents._Utils import speak
import json


class _ChatAgent():
    def __init__(self, llm=None):
        self.lema_output_history = []
        
        self.llm = llm
        self.history = [
            {"role": "system", "content": ''' You are Lema, the personal and intelligent Local Efficient Multitasking Assistant. You work with cooperation with other agents to provide the best user experience. You are the frontman of this project, therefore all questions you receive , you must answer as first person. 
             You are equiped with the ability to interact with the Windows operating system. Although you are not a computer, you can use it to perform various tasks on demand. Do not repeat yourself to save the PC's memory. '''},
        ]
        self.conversation_file = 'conversation.json'
        

    def send_message(self, user_input):
        self.history.append({"role": "user", "content": user_input})

        completion = self.llm.create_chat_completion(
            self.history,
            temperature=0.6,
            stream=True,
            repeat_penalty=1,
            seed=-1,
            max_tokens=2048
        )

        assistant_response = ""
        temp_sentence = ""

        for chunk in completion:
            delta = chunk['choices'][0]['delta']
            
            if 'content' in delta:
                chunk_content = delta['content']
                assistant_response += chunk_content
                temp_sentence += chunk_content

                if len(assistant_response) > 450:
                    if temp_sentence.endswith(('.', '!', '?')):
                        speak(temp_sentence)
                        temp_sentence = ""
                elif len(assistant_response) <= 450:
                    temp_sentence = assistant_response

        if temp_sentence:
            if temp_sentence.endswith(('.', '!', '?')):
                speak(temp_sentence)
            else:
                speak(temp_sentence)

        self.history.append({"role": "assistant", "content": assistant_response.strip()})
        
        with open(self.conversation_file, 'a') as f:
            json.dump(self.history, f, indent=4)
        return assistant_response