from faster_whisper import WhisperModel
import pyaudio, wave, audioop, time

class SpeechToText:
    def __init__(self, model_size="distil-large-v3", threshold=330):
        self.model_size = model_size
        self.threshold = threshold
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 48000
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
        silence_start_time = time.time()
        recording = False
        while True:
            data = self.stream.read(self.CHUNK)
            rms = audioop.rms(data, 2)
            if rms > self.threshold:
                if not recording:
                    print("Recording...")
                    recording = True
                frames.append(data)
                silence_start_time = time.time()
            else:
                if recording:
                    if time.time() - silence_start_time > 3:  # 3 seconds of silence to stop recording
                        break
                    else:
                        frames.append(data)
                else:
                    print("Waiting for audio...", end="\r", flush=True)

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