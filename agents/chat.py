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
            stream=False,
            repeat_penalty=1,
            seed=-1,
            max_tokens=2048
        )
        previous_assistant_response = ''
        _assistant_response = completion['choices'][0]['message']['content']
        assistant_response = _assistant_response.strip().lower()
        previous_assistant_response = self.history[-2]['content'] if len(self.history) > 1 else ''

        # Check if the assistant response is too long to be spoken in one go
        if len(assistant_response) > 300:
            
            sentences = assistant_response.split('. ')  # If it is, split the response into individual sentences
            processed_sentences = []    # Initialize an empty list to store the processed sentences
            temp_sentence = ''  # Initialize an empty string to build up sentences that are 300 characters or less
            
            # Iterate over each sentence
            for sentence in sentences:
                
                sentence += '. '    # Add a period and a space to the end of the sentence
            
                if len(temp_sentence) + len(sentence) <= 300:   # Check if adding the sentence to temp_sentence would make it too long
                    temp_sentence += sentence   # If not, add the sentence to temp_sentence
                else:
                    processed_sentences.append(temp_sentence.strip())   # If it would, add temp_sentence to the processed sentences and reset temp_sentence
                    temp_sentence = sentence
            
            # Add the last temp_sentence to the processed sentences if it's not empty
            if temp_sentence:
                processed_sentences.append(temp_sentence.strip())
            
            # Speak each sentence in the processed sentences
            for sentence_to_speak in processed_sentences:
                speak(sentence_to_speak)

        else:
            # If the assistant response is 300 characters or less, just speak it
            speak(assistant_response)

        # Print the assistant_response
        print(assistant_response)

        self.history.append({"role": "assistant", "content": assistant_response.strip()})
        with open('lema_last_reply.txt', 'w') as f:
            f.write(previous_assistant_response)
        with open(self.conversation_file, 'w') as f:
            json.dump(self.history, f, indent=4)
        return _assistant_response