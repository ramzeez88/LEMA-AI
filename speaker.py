import asyncio
import edge_tts
import pygame


# pl-PL-ZofiaNeural , pl-PL-MarekNeural , en-US-JennyNeural , en-NZ-MollyNeural , en-NG-AbeoNeural , en-IE-ConnorNeural

class Speaker:
    def __init__(self, ai_text, voice="en-US-JennyNeural", output_file="lema.mp3"):  
        self.ai_text = ai_text
        self.voice = voice
        self.output_file = output_file

    async def speak(self) -> None:
        communicate = edge_tts.Communicate(self.ai_text, self.voice, pitch="+6Hz", rate="+20%", volume="+0%")
        await communicate.save(self.output_file)
        # Initialize pygame
        pygame.init()

        # Load the MP3 file
        pygame.mixer.music.load(self.output_file)

        # Play the MP3 file
        pygame.mixer.music.play()

        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Clean up
        pygame.quit()

if __name__ == "__main__":
    text = '''I was right you were wrong.'''
    speaker = Speaker(text)
    asyncio.run(speaker.speak())
