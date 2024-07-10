from agents._Utils import  speak
from agents._Utils import Timer
import os, pyautogui, webbrowser, time, threading,json , keyboard
from datetime import datetime
import pyperclip




class _FunctionAgent:
    def __init__(self,llm):
        self.client = llm
        self.timer = Timer(None,None,None)
    def extract_command(self, user_input):
        function_call = self.execute_command(user_input)
        command = ""  # Define command with a default value
        if "<" in function_call:
            command = function_call.split("<")[1].split(">")[0].lower()
        return command

    def execute_command(self, user_input):
        function_call_response = self.client.create_chat_completion(
            
            messages=[
                {"role": "system", "content": '''You are a helpful AI assistant. I want you to call function names depending on the input you recieve. The list of commands that you can use: 
                '<open_web_browser>' for opening web browser , '<open_web_browser_url>' for opening web browser with a specific url,'<open_file_browser>' for opening file browser , '<open_cmd>' for opening cmd, '<open_calculator>' for opening calculator,
                '<open_notepad>' for opening notepad, '<open_calendar>' for opening calendar, '<open_mail>' for opening mail,'<current_time>' for getting current time,'<current_date>' for getting current date,'<save_last_reply>' for saving last reply when writing stories,'<set_timer>' for setting timer.
                To close current window, use '<close_window>'.When you are asked to close last window, use '<close_last_window>'.To exit ,use '<exit>'.
                Your responses must contain only the appropriate function name.'''},
                {"role": "user", "content": "Can you open a web browser for me?"},
                {"role": "assistant", "content": "<open_web_browser>"},
                {"role": "user", "content": "open a file browser"},
                {"role": "assistant", "content": "<open_file_browser>"},
                {"role": "user", "content": "thanks, now close it"},
                {"role": "assistant", "content": "<close_last_window>"},
                {"role": "user", "content": "open roblox.com"},
                {"role": "assistant", "content": "<open_web_browser_url>"},
                {"role": "user", "content": "please open cmd"},
                {"role": "assistant", "content": "<open_cmd>"},
                {"role": "user", "content": "can you save it to a notepad ?"},
                {"role": "assistant", "content": "<save_last_reply>"},
                {"role": "user", "content": "can you open the calculator ?"},
                {"role": "assistant", "content": "<open_calculator>"},
                {"role": "user", "content": " exit now"},
                {"role": "assistant", "content": "<exit>"},
                {"role": "user", "content": "close current window"},   
                {"role": "assistant", "content": "<close_window>"},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            stream=False,
            max_tokens=20
        )

        function_call = function_call_response['choices'][0]['message']['content'].strip().lower()
        
        return function_call


            
    def _execute_function(self, command,user_input=None):
        if command == "open_web_browser":
            webbrowser.open_new_tab("https://www.google.com")
        elif command == "open_web_browser_url":
            words = user_input.lower().split()
            url = words[-1]
            url = url.strip('?')  # remove the '?' at the end of the URL
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
                webbrowser.open_new_tab(url)
        elif command == "save_last_reply":
            self.save_last_reply()
        elif command == "open_file_browser":
            os.startfile(".")
        elif command == "open_cmd":
            os.system("start cmd")
        elif command == "open_calculator":
            os.system("start calc")
        elif command == "open_notepad":
            os.system("start notepad")
        elif command == "open_calendar":
            os.system("start outlookcal:")
        elif command == "open_mail":
            os.system("start outlookmail:")
        elif command == "close_window":
            pyautogui.hotkey('alt', 'f4')
        elif command == "close_last_window":
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.05)
            pyautogui.hotkey('alt', 'f4')
        elif command == "exit":
            os._exit(0)
        elif command == "set_timer":
           print(user_input)
           self.timer.set_timer(user_input)
        elif command == "current_time":
            _time = datetime.now().strftime("%H:%M")
            speak("The time is " + _time)
        elif command == "current_date":
            date = datetime.now().strftime("%Y-%m-%d")
            speak("The date is " + date)
        else:
            print("Unknown command")


    

    def save_last_reply(self):
        try:
            # Read the conversation file
            with open('conversation.json', 'r') as file:
                conversation = json.load(file)
            
            # Find assistant replies
            assistant_replies = [message for message in conversation if message['role'] == 'assistant']
            
            # Check if there are at least two assistant replies
            if len(assistant_replies) >= 2:
                # Get the second last assistant reply
                second_last_reply = assistant_replies[-2]['content']
                
                # Open Notepad
                os.system("start notepad")
                time.sleep(0.5)  # wait for Notepad to start (adjust the delay as needed)
                
                # Copy the reply to clipboard and paste it into Notepad
                pyperclip.copy(second_last_reply)
                keyboard.press_and_release('ctrl+v')
                
                # Switch back to the previous window
                keyboard.press_and_release('alt+tab')
                
                # print("Second last assistant's reply saved to Notepad.")
            else:
                print("Not enough assistant replies in the conversation.")
        
        except FileNotFoundError:
            print("Conversation file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON from the conversation file.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    
    
    def add_memo(self, memo):
        # Add the memo to the list of memos
        pass
  