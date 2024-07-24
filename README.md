# LEMA AI - Local Efficient Multitasking Assistant v0.0.1
My take on creating an inteligent local assistant with some 'superpowers'. I have tested it on Windows OS only.

Reqirements for python 3.11 :  
- Windows 10/11 OS,
- cuda enabled device with cuda 12.1 support, cuda toolkit from https://developer.nvidia.com/cuda-12-1-0-download-archive  and  then install CUDNN from https://developer.nvidia.com/cudnn, my nvidia driver version 546.33
- Visual Studio Build Tools 2022 ('Desktop Development with C++' ticked and installed),
- conda installed and virtual environment created,
- pytorch with cuda installed pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --no-build-isolation,
- llama-cpp-python (min Version: 0.2.75 , whl file can be downloaded from their releases page),
- pip3 install faster-whisper --no-build-isolation,
- git clone this repo
- git clone OpenVoice from here https://github.com/myshell-ai/OpenVoice/tree/main to LemaAI folder and the checkpoints can be downloaded from https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_1226.zip then extracted to checkpoints folder in OpenVoice (not openvoice) folder.
- move 'lema.mp3' to 'OpenVoice/resources' folder.
- move 'open_voice_main.py' to OpenVoice folder.

If you are not worried about sensitive data leaving your computer and/or have less than 12GB VRAM, you can use edge_tts module in python to convert text to speech using Microsoft compute. All you have to do is pip install edge_tts asyncio pygame. 
               
            

Licence not decided yet.

Please support me on ko-fi.com/ramzeez88  :)
