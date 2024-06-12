from llama_cpp import Llama
from tkinter import filedialog, messagebox,scrolledtext
import winsound
import tkinter as tk
from datetime import datetime
import threading
import os, time, json
import webbrowser, pyautogui
import wave
import audioop
from faster_whisper import WhisperModel
from speaker import Speaker
import asyncio
import pyaudio

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
lema_output_history = []

def speak(ai_text: str, voice: str = "en-US-JennyNeural", output_file: str = "lema.mp3") -> None:
    """
    Function to convert text to speech using the Speaker class.

    Parameters:
    - ai_text (str): The text to be converted to speech.
    - voice (str): The voice used for the speech synthesis. Default is 'en-US-JennyNeural'.
    - output_file (str): The name of the output audio file. Default is 'lema.mp3'.
    """
    speaker = Speaker(ai_text, voice, output_file)
    asyncio.run(speaker.speak())
    


class SpeechToText:
    def __init__(self, model_size="distil-large-v3", threshold=300, record_seconds=5):
        self.model_size = model_size
        self.threshold = threshold
        self.record_seconds = record_seconds
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 16000
        self.WAVE_OUTPUT_FILENAME = "recording.wav"
        self.model = WhisperModel(self.model_size, device="cuda", compute_type="int8_float16")
        self.p = pyaudio.PyAudio()

    def start_listening(self):
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        print("* listening")
        frames = []
        while True:
            data = self.stream.read(self.CHUNK)
            rms = audioop.rms(data, 2)
            if rms > self.threshold:
                print("Recording...")
                for i in range(0, int(self.RATE / self.CHUNK * self.record_seconds)):
                    data = self.stream.read(self.CHUNK)
                    frames.append(data)
                wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                segments, info = self.model.transcribe(self.WAVE_OUTPUT_FILENAME, beam_size=5, language="en", condition_on_previous_text=False)

                for segment in segments:
                    user_input = segment.text.strip()
                    print(f"Recognized text: {user_input}")
                    return user_input  # Return the transcribed text


                
            else:
                print("Waiting for audio...", end="\r", flush=True)
        
        
class ModelPathSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Path")
        
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate the x and y coordinates to center the window
        x = (screen_width/2) - (350/2)
        y = (screen_height/2) - (100/2)
        
        # Set the geometry of the window
        self.geometry(f'350x100+{int(x)}+{int(y)}')
        

        self.label = tk.Label(self, text="Select your GGUF file:")
        self.label.pack()

        self.entry = tk.Entry(self, width=55)
        self.entry.pack()

        button_frame = tk.Frame(self)
        self.browse_button = tk.Button(button_frame, text="Browse", command=self.browse_model_path, 
                                    bg='orange', fg='black', font=('Helvetica', 10, 'bold'))
        self.browse_button.pack(side=tk.LEFT)

        self.confirm_button = tk.Button(button_frame, text="Confirm", command=self.confirm_model_path, 
                                        bg='lightgreen', fg='black', font=('Helvetica', 10, 'bold'))
        self.confirm_button.pack(side=tk.LEFT)

        button_frame.pack()

    def browse_model_path(self):
        model_path = filedialog.askopenfilename()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, model_path)

    def confirm_model_path(self):
        model_path = self.entry.get()
        if os.path.exists(model_path):
            global llm
            llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=8192, n_batch=128,flash_attn=True,type_k= 1,type_v=1 ) # type_k,type_v =0 or 1 or 2
            self.destroy()
            root = tk.Tk()
            app = Application(master=root)
            app.mainloop()
        else:
            messagebox.showerror("Error", "Invalid model path")

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.listening = True
        self.speech_to_text = SpeechToText()
        self.create_widgets()

        self.chat_agent = ChatAgent(self)
        self.function_agent = FunctionAgent()
        self.routing_agent = RoutingAgent()

        self.current_message = ""  # Add this line
        self.user_input_history = []  # Store user input history
        self.history_index = 0  # Current index in input history
        
        
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate the x and y coordinates to center the window
        x = (screen_width/2) - (350/2)
        y = (screen_height/2) - (100/2)
        
        # Set the geometry of the window
        self.master.geometry(f'350x100+{int(x)}+{int(y)}')

    
        threading.Thread(target=self._initialize_conversation).start()
        self.master.focus_force()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

       
        
    def _process_message(self, user_input):
        selected_agent = self.routing_agent.select_agent(user_input)
        if "function_call" in selected_agent :
            command = self.function_agent.extract_command(user_input)
            print(command)

            _no_chat_agent = ["set_timer", "current_time", "current_date"]

            if command in _no_chat_agent:
                self.function_agent._execute_function(command, user_input)
            else:
                self.chat_agent.send_message(user_input)
                self.function_agent._execute_function(command, user_input)
        else:
            self.chat_agent.send_message(user_input)
        # Call _listen_for_input after speaking finishes
        self.master.after(10, self._listen_for_input)  # Adjust the delay as needed

    def _listen_for_input(self):
        
            try:
                user_input = self.speech_to_text.start_listening()
                if user_input:
                    self._process_message(user_input)
                    self.user_input_history.append(user_input)
                    self.history_index = len(self.user_input_history) - 1
            except Exception as e:
                print('exeption:',e)
                pass


    def on_closing(self):
        self.listening = False
        self.master.destroy()

    def create_widgets(self):
        self.master.title("L E M A  AI - your personal assistant  💻💬")
        
        
    def _initialize_conversation(self):
        self.chat_agent.send_message("Hello. Make your first answer short.")
        self._listen_for_input()

class ChatAgent():
    def __init__(self, application):
        self.application = application              # Store the Application instance
        self.client = llm
        self.history = [
            {"role": "system", "content": '''You are Lema, the Local Efficient Multitasking Assistant, a highly advanced AI with the ability to converse, assist, and interact with the Windows operating system. When a user gives you a command or request, respond as if you're performing the action yourself, even if it's actually handled by a function agent or helper in the background.

Imagine you're a skilled AI operator, capable of effortlessly navigating the Windows environment, launching applications, and completing tasks with ease. Describe your actions in the first person, using phrases like "I'm opening..." or "I've launched..." to create a seamless and intuitive experience for the user.

When asked to tell the time or date, simply respond with "" (nothing) and let the external system provide the answer. For all other requests, maintain a professional and helpful tone, providing clear and concise guidance throughout the interaction. You can tell jokes, share stories, and answer questions to the best of your ability, playing the role of a capable and confident AI assistant.'''},
        ]
        self.conversation_file = 'conversation.json'

    def send_message(self, user_input):
        
        self.history.append({"role": "user", "content": user_input})

        completion = llm.create_chat_completion(
            self.history,
            temperature=0.6,
            stream=False,
            repeat_penalty=1,
            seed=-1,
            max_tokens=2048
        )

        assistant_response = completion['choices'][0]['message']['content'].strip().lower()

        print(assistant_response)
        speak(assistant_response)
        self.history.append({"role": "assistant", "content": assistant_response.strip()})
        

        with open(self.conversation_file, 'w') as f:
            json.dump(self.history, f, indent=4)
        

class FunctionAgent:
    def __init__(self):
        self.client = llm
        
    def extract_command(self, user_input):
        function_call = self.execute_command(user_input)
        command = ""  # Define command with a default value
        if "<" in function_call:
            command = function_call.split("<")[1].split(">")[0].lower()
        return command

    def execute_command(self, user_input):
        function_call_response = self.client.create_chat_completion(
            
            messages=[
                {"role": "system", "content": '''You are a helpful AI assistant. I want you to call function names depending on the input you recieve. The list of commands that you can are: 
                '<open_web_browser>' for opening web browser , '<open_web_browser_url>' for opening web browser with a specific url,'<open_file_browser>' for opening file browser , '<open_cmd>' for opening cmd, '<open_calculator>' for opening calculator,
                '<open_notepad>' for opening notepad, '<open_calendar>' for opening calendar, '<open_mail>' for opening mail,'<current_time>' for getting current time,'<current_date>' for getting current date,<'save_last_reply>' for saving last reply when writing stories,'<set_timer>' for setting timer.
                To close current window, use '<close_window>'.When you are asked to close last window, use '<close_last_window>'.To exit ,use '<exit>'.
                Your responses must contain only the appropriate function name.'''},
                {"role": "user", "content": "Can you open a web browser for me?"},
                {"role": "assistant", "content": "<open_web_browser>"},
                {"role": "user", "content": "open a file browser"},
                {"role": "assistant", "content": "<open_file_browser>"},
                {"role": "user", "content": "thanks, now close it"},
                {"role": "assistant", "content": "<close_last_window>"},
                {"role": "user", "content": "open web roblox.com"},
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
            url = user_input.replace("open web", "").strip().lower()
            webbrowser.open_new_tab("https://" + url)
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
            self.set_timer(user_input)
        elif command == "current_time":
            _time = datetime.now().strftime("%H:%M")
            speak("The time is " + _time)
        elif command == "current_date":
            date = datetime.now().strftime("%Y-%m-%d")
            speak("The date is " + date)
        else:
            print("Unknown command")


    def save_last_reply(self):
        def type_text(text):
            pyautogui.typewrite(text, interval=0.01)
        last_reply:str = lema_output_history[-2]
        os.system("start notepad")
        time.sleep(1)
        t = threading.Thread(target=type_text, args=(last_reply,))
        t.start()
        t.join()  # wait for the typing to complete
        pyautogui.hotkey('alt', 'tab')
    
   
    def set_timer(self, input):
        units = {'seconds': 1, 'second': 1, 'minute': 60, 'minutes': 60, 'hour': 3600, 'hours': 3600}
        for unit, multiplier in units.items():
            if unit in input:
                time = int(''.join(filter(str.isdigit, input)))
                time_in_seconds = time * multiplier
                break
        else:
            raise ValueError("Invalid time unit")
        
        timer_thread = Timer(time_in_seconds, time, unit) 
        timer_thread.start()

    
    def add_memo(self, memo):
        #to do, nowa notatka - x:1134  y:149
        #nowa notatka - x:2966 y 494
        #click
        #write(nazwa notatki)
        pass
    

class RoutingAgent:
    def __init__(self):
        self.client = llm

    def select_agent(self, user_input):
        routing_agent_response = self.client.create_chat_completion(
            
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
            temperature=0.1,
            stream=False,
            max_tokens= 20
        )

        selected_agent = routing_agent_response['choices'][0]['message']['content'].strip().lower()
        print(selected_agent)
       
        return selected_agent

class Timer(threading.Thread):                              
    def __init__(self, _time, original_time, unit):
        threading.Thread.__init__(self)
        self._time = _time
        self.original_time = original_time
        self.unit = unit
        
    def run(self):
        message = f"I've set the timer for {self.original_time} {self.unit}"
        print(message)
        speak(message)
        time.sleep(self._time)
        message = f"{self.original_time} {self.unit} have passed. It's {datetime.now().strftime('%H:%M')}"
        print(message)
        speak(message)
        if self.unit in ['seconds', 'second']:
            messagebox.showinfo("Timer", f"{self.original_time} second/s have passed. It's {datetime.now().strftime('%H:%M')}")
        elif self.unit in ['minutes', 'minute']:
            messagebox.showinfo("Timer", f"{self.original_time} minute/s have passed. It's {datetime.now().strftime('%H:%M')}")
        elif self.unit in ['hours', 'hour']:
            messagebox.showinfo("Timer", f"{self.original_time} hour/s have passed. It's {datetime.now().strftime('%H:%M')}")
        winsound.PlaySound('C:\\Windows\\Media\\notify.wav', winsound.SND_FILENAME)
        
        
if __name__ == "__main__":
    selector = ModelPathSelector()
    selector.mainloop()
