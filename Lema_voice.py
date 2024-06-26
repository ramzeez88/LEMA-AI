

# Standard library imports
import os
# Third-party library imports
import tkinter as tk
from tkinter import messagebox , filedialog

# Local modules imports
from llama_cpp import Llama

# Custom agents imports
from agents.function import _FunctionAgent as FunctionAgent
from agents.routing import _RoutingAgent as RoutingAgent
from agents.chat import _ChatAgent as ChatAgent
from agents.speech_to_text import SpeechToText
from OpenVoice.open_voice_main import TextToSpeech

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'


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
            ''' Args:
            model_path: Path to the model.
            n_gpu_layers: Number of layers to offload to GPU (-ngl). If -1, all layers are offloaded.
            split_mode: How to split the model across GPUs. See llama_cpp.LLAMA_SPLIT_* for options.
            main_gpu: main_gpu interpretation depends on split_mode: LLAMA_SPLIT_NONE: the GPU that is used for the entire model. LLAMA_SPLIT_ROW: the GPU that is used for small tensors and intermediate results. LLAMA_SPLIT_LAYER: ignored
            tensor_split: How split tensors should be distributed across GPUs. If None, the model is not split.
            vocab_only: Only load the vocabulary no weights.
            use_mmap: Use mmap if possible.
            use_mlock: Force the system to keep the model in RAM.
            kv_overrides: Key-value overrides for the model.
            seed: RNG seed, -1 for random
            n_ctx: Text context, 0 = from model
            n_batch: Prompt processing maximum batch size
            n_threads: Number of threads to use for generation
            n_threads_batch: Number of threads to use for batch processing
            rope_scaling_type: RoPE scaling type, from `enum llama_rope_scaling_type`. ref: https://github.com/ggerganov/llama.cpp/pull/2054
            pooling_type: Pooling type, from `enum llama_pooling_type`.
            rope_freq_base: RoPE base frequency, 0 = from model
            rope_freq_scale: RoPE frequency scaling factor, 0 = from model
            yarn_ext_factor: YaRN extrapolation mix factor, negative = from model
            yarn_attn_factor: YaRN magnitude scaling factor
            yarn_beta_fast: YaRN low correction dim
            yarn_beta_slow: YaRN high correction dim
            yarn_orig_ctx: YaRN original context size
            logits_all: Return logits for all tokens, not just the last token. Must be True for completion to return logprobs.
            embedding: Embedding mode only.
            offload_kqv: Offload K, Q, V to GPU.
            flash_attn: Use flash attention.
            last_n_tokens_size: Maximum number of tokens to keep in the last_n_tokens deque.
            lora_base: Optional path to base model, useful if using a quantized base model and you want to apply LoRA to an f16 model.
            lora_path: Path to a LoRA file to apply to the model.
            numa: numa policy
            chat_format: String specifying the chat format to use when calling create_chat_completion.
            chat_handler: Optional chat handler to use when calling create_chat_completion.
            draft_model: Optional draft model to use for speculative decoding.
            tokenizer: Optional tokenizer to override the default tokenizer from llama.cpp.
            verbose: Print verbose output to stderr.
            type_k: KV cache data type for K (default: f16)
            type_v: KV cache data type for V (default: f16) '''
            llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=8192, n_batch=120,flash_attn=True,type_k= 1,type_v=1 ) # type_k,type_v =0 or 1 or 2
            self.destroy()
            
        else:
            messagebox.showerror("Error", "Invalid model path")
        
  
class Application:
    def __init__(self, llm):
        self.llm = llm
        self.listening = True
        self.speech_to_text = SpeechToText()
        self.text_to_speech = TextToSpeech()
        self.chat_agent = ChatAgent(llm)  # Pass self and llm as arguments
        self.function_agent = FunctionAgent(llm)
        self.current_message = ""  
        self.user_input_history = []  
        self.history_index = 0  

        
    def _process_message(self, user_input):
        selected_agent = RoutingAgent(llm).select_agent(user_input)
        if "function_call" in selected_agent:
            command = FunctionAgent(llm).extract_command(user_input)
            print(command)

            _no_chat_agent = ["set_timer", "current_time", "current_date"]

            if command in _no_chat_agent:
               self.function_agent._execute_function(command, user_input)
            else:
                
                self.chat_agent.send_message(user_input)
                self.function_agent._execute_function(command, user_input)
        else:
            
            self.chat_agent.send_message(user_input)
        self._listen_for_input()       

    def _listen_for_input(self):
        
        try:
            user_input = self.speech_to_text.start_listening()
            if user_input:
                self._process_message(user_input)
                self.user_input_history.append(user_input)
                self.history_index = len(self.user_input_history) - 1
        except Exception as e:
            print('exeption:', e)
            pass


    def on_closing(self):
        self.listening = False
    

if __name__ == "__main__":
    selector = ModelPathSelector()
    selector.mainloop()
    app = Application(llm)
    app.chat_agent.send_message("Hello.")
    app._listen_for_input()  
    while True:
        # Keep the application running until it's stopped manually
        pass