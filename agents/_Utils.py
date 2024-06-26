from OpenVoice.open_voice_main import TextToSpeech
import asyncio, threading , time, winsound
from datetime import datetime
from tkinter import messagebox
from word2number.w2n import word_to_num



tts = TextToSpeech()



def speak(text_to_synthesize):
    """
    Speak the given text using the Text-to-Speech (TTS) system.

    Args:
        text_to_synthesize (str): The text to be synthesized into speech.

    Returns:
        None

    This function uses the TextToSpeech (TTS) system to convert the given text into speech. The TTS system have a method called `run_inference` that takes the text as input and generates the corresponding speech.

    Example usage:
        speak("Hello, how are you?")
    """
    tts.run_inference(text_to_synthesize)
    




class Timer:
    def __init__(self, _time, original_time, unit):
        self._time = _time
        self.original_time = original_time
        self.unit = unit

    def run(self):
        message = f"I've set the timer for {self.original_time} {self.unit}"
        print(message)
        speak(message)
        time.sleep(self._time)  # time.sleep
        winsound.PlaySound('C:\\Windows\\Media\\notify.wav', winsound.SND_FILENAME)
        message = f"{self.original_time} {self.unit} have passed. It's {datetime.now().strftime('%H:%M')}"
        speak(message)
   
    @staticmethod
    def set_timer(input):
        units = {'seconds': 1, 'second': 1, 'minute': 60, 'minutes': 60, 'hour': 3600, 'hours': 3600}
        for unit, multiplier in units.items():
            if unit in input:
                words = input.split()
                for word in words:
                    if word.isdigit():
                        time = int(word)
                        time_in_seconds = time * multiplier
                        break
                    else:
                        try:
                            time = word_to_num(word)
                            time_in_seconds = time * multiplier
                            break
                        except ValueError:
                            pass
                else:
                    messagebox.showerror("Error", "Invalid time. Please enter a numeric value or a written number.")
                    return
                break
        else:
            messagebox.showerror("Error", "Invalid time unit. Please enter seconds, minute, hour, or their plurals.")
            return

        timer_thread = Timer(time_in_seconds, time, unit)
        threading.Thread(target=timer_thread.run).start()  # Run the timer in a separate thread

    
