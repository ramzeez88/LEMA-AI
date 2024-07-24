from speaker import Speaker
import asyncio, threading , time, winsound
from datetime import datetime
from tkinter import messagebox
from word2number.w2n import word_to_num







def speak(ai_text: str, voice: str = "en-US-JennyNeural", output_file: str = "try.mp3") -> None:
   speaker = Speaker(ai_text, voice, output_file)
   asyncio.run(speaker.speak())
    


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

    
