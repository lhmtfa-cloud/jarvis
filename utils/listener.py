import pyaudio
import threading
import wave
import os
import time
import numpy as np
import ctranslate2
from transformers import AutoProcessor

class AudioListener:
    def __init__(self, model_id_original, model_path_local, text_queue, config, compute_type="int8", beam_size=1):
        self.model_id_original = model_id_original
        self.model_path_local = model_path_local
        self.text_queue = text_queue
        self.config = config
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event() 
        self.listening_thread = None
        self.compute_type = compute_type
        self.beam_size = beam_size

        self.processor = None
        self.model = None

    def _load_model(self):
        try:
            print(f"Carregando o PROCESSADOR de áudio de '{self.model_id_original}'...")
            self.processor = AutoProcessor.from_pretrained(self.model_id_original)
            print("Processador carregado com sucesso.")

            print(f"Carregando o MODELO OTIMIZADO de '{self.model_path_local}'...")
            self.model = ctranslate2.models.Whisper(self.model_path_local, device="cpu", compute_type=self.compute_type)
            print(f"Modelo otimizado carregado com sucesso! (Device: cpu, Compute Type: {self.compute_type})")
            return True
        except Exception as e:
            error_message = f"ERRO ao carregar o modelo/processador: {e}"
            print(error_message)
            self.text_queue.put({"type": "error", "text": error_message})
            return False

    def _listen_and_transcribe(self):
        if not self.model and not self._load_model():
            return

        self.stream = self.p.open(
            format=self.config['FORMAT'], channels=self.config['CHANNELS'],
            rate=self.config['RATE'], input=True,
            frames_per_buffer=self.config['CHUNK_SIZE']
        )
        print(">>> Assistente pronto e ouvindo... <<<")

        while not self.stop_event.is_set():
            
            if self.pause_event.is_set():
                time.sleep(0.1)
                continue
            
            frames = []
            is_speaking = False
            
            while not self.stop_event.is_set():
                
                if self.pause_event.is_set():
                    is_speaking = False 
                    break 
                
                try:
                    data = self.stream.read(self.config['CHUNK_SIZE'], exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    volume = np.sqrt(np.mean(audio_data.astype(float)**2))
                    if volume > self.config['SILENCE_THRESHOLD']:
                        is_speaking = True
                        frames.append(data)
                        break 
                except IOError: continue
            
            if not is_speaking:
                continue

            silent_chunks = 0
            max_silent_chunks = (self.config['RATE'] / self.config['CHUNK_SIZE']) * self.config['SILENCE_DURATION']
            
            while not self.stop_event.is_set():
                
                if self.pause_event.is_set():
                    frames = [] 
                    break 
                
                try:
                    data = self.stream.read(self.config['CHUNK_SIZE'], exception_on_overflow=False)
                    frames.append(data)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    volume = np.sqrt(np.mean(audio_data.astype(float)**2))
                    if volume > self.config['SILENCE_THRESHOLD']:
                        silent_chunks = 0
                    else:
                        silent_chunks += 1
                    
                    if silent_chunks > max_silent_chunks:
                        self._process_audio(b''.join(frames))
                        break 
                except IOError: continue

        if self.stream: self.stream.stop_stream(); self.stream.close()
        self.p.terminate()
        print(">>> Processo de escuta finalizado. <<<")

    def _process_audio(self, audio_bytes):
        if self.pause_event.is_set():
            return
        
        t_start_transcribe = time.time()
        self.text_queue.put({
            "type": "status", 
            "text": "Transcrevendo...", 
            "duration": 0
        })
        
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            features = self.processor(audio_array, sampling_rate=self.config['RATE'], return_tensors="np").input_features
            features_ct2 = ctranslate2.StorageView.from_array(features)

            sot_token_id = self.processor.tokenizer.convert_tokens_to_ids("<|startoftranscript|>")
            lang_token_id = self.processor.tokenizer.convert_tokens_to_ids("<|pt|>")
            task_token_id = self.processor.tokenizer.convert_tokens_to_ids("<|transcribe|>")
            prompt_ids = [sot_token_id, lang_token_id, task_token_id]

            results = self.model.generate(features_ct2, [prompt_ids], beam_size=self.beam_size)
            
            texto = self.processor.batch_decode(results[0].sequences_ids, skip_special_tokens=True)[0].strip()
            
            t_end_transcribe = time.time()
            duration = t_end_transcribe - t_start_transcribe
            
            if texto:
                self.text_queue.put({
                    "type": "text", 
                    "text": texto, 
                    "last_stage": "Transcrição",
                    "duration": round(duration, 2)
                })
            else:
                self.text_queue.put({
                    "type": "status", 
                    "text": "Ouvindo...", 
                    "last_stage": "Transcrição (Vazia)",
                    "duration": round(duration, 2)
                })

        except Exception as e:
            self.text_queue.put({"type": "error", "text": f"ERRO na transcrição: {e}"})

    def start(self):
        if self.listening_thread is None or not self.listening_thread.is_alive():
            self.stop_event.clear()
            self.pause_event.clear()
            self.listening_thread = threading.Thread(target=self._listen_and_transcribe, daemon=True)
            self.listening_thread.start()

    def stop(self):
        self.stop_event.set()

    def pause(self):
        self.pause_event.set()
        print(">>> Processamento de áudio pausado. <<<")

    def resume(self):
        self.pause_event.clear()
        print(">>> Processamento de áudio retomado. <<<")