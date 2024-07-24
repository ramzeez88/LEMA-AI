import os
import torch
from OpenVoice.openvoice import se_extractor
from OpenVoice.openvoice.api import BaseSpeakerTTS, ToneColorConverter
import os
import pygame

class TextToSpeech:
    def __init__(self):
        self.ckpt_base = 'OpenVoice/checkpoints/base_speakers/EN'
        self.ckpt_converter = 'OpenVoice/checkpoints/converter'
        self.device =    "cuda:0" #  "cuda:0" if torch.cuda.is_available() else "cpu"         # 
        self.base_speaker_tts = BaseSpeakerTTS(f'{self.ckpt_base}/config.json', device=self.device)
        self.base_speaker_tts.load_ckpt(f'{self.ckpt_base}/checkpoint.pth')
        self.tone_color_converter = ToneColorConverter(f'{self.ckpt_converter}/config.json', device=self.device)
        self.tone_color_converter.load_ckpt(f'{self.ckpt_converter}/checkpoint.pth')
        self.source_se = torch.load(f'{self.ckpt_base}/en_style_se.pth').to(self.device)
        self.reference_audio_path = 'OpenVoice/resources/lema.mp3'
        self.output_path = 'OpenVoice\\outputs'

    def run_inference(self, text_to_synthesize):
        target_se, audio_name = se_extractor.get_se(self.reference_audio_path, self.tone_color_converter, target_dir='processed', vad=True)
        tmp_path = os.path.join(self.output_path, 'output.mp3')
        self.base_speaker_tts.tts(text_to_synthesize, tmp_path, speaker='friendly', language='English', speed=1.2)  # ['default', 'whispering', 'shouting', 'excited', 'cheerful', 'terrified', 'angry', 'sad', 'friendly']
        encode_message = "@MyShell"
        save_path = self.output_path
        self.tone_color_converter.convert(
            audio_src_path=tmp_path, 
            src_se=self.source_se, 
            tgt_se=target_se, 
            output_path=os.path.join(self.output_path, '\\output.mp3'),
            message=encode_message)
        # print(f"Output saved to {save_path}")
        self.play_output_audio(self.output_path)

    def play_output_audio(self, output_path):
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(output_path, '\\output.mp3'))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(3)
        pygame.mixer.quit()                                                  # this line releases the output.mp3 file

# Example usage
#tts = TextToSpeech()
#text_to_synthesize = "Hi my name is Lema. I am an intelligent multitasking assistant who can help you with your day to day tasks on windows machine!"
#tts.run_inference(text_to_synthesize)