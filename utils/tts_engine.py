import pyttsx3
import threading
import queue
import time

class TTSWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.is_enabled = True
        self.engine = None
        try:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
        except Exception as e:
            print(f"Erro ao inicializar thread TTS: {e}")
            self.is_enabled = False

    def _run(self):
        try:
            self.engine = pyttsx3.init()
        except Exception as e:
            print(f"Erro fatal ao inicializar pyttsx3: {e}")
            self.is_enabled = False
            return 

        while True:
            try:
                text, on_done_callback = self.queue.get()
                
                if self.is_enabled and self.engine:
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                if on_done_callback:
                    on_done_callback()
                    
            except Exception as e:
                print(f"Erro no loop do worker TTS: {e}")
                try:
                    # Tenta reiniciar o engine se falhar
                    self.engine = pyttsx3.init()
                except Exception as re_e:
                    print(f"Falha ao re-inicializar engine TTS: {re_e}")
                    self.is_enabled = False
                    time.sleep(1) # Evita loop de falha rápido

    def submit_talk(self, texto: str, on_done_callback=None):
        if self.is_enabled:
            self.queue.put((texto, on_done_callback))
        elif on_done_callback:
            on_done_callback()

    def set_enabled(self, status: bool):
        self.is_enabled = status

try:
    _tts_worker_instance = TTSWorker()
    is_functional = _tts_worker_instance.is_enabled
except Exception as e:
    print(f"Falha ao criar instância do TTSWorker: {e}")
    _tts_worker_instance = None
    is_functional = False

def set_enabled(status: bool):
    if _tts_worker_instance:
        _tts_worker_instance.set_enabled(status)

def falar(texto: str, on_done_callback=None):
    if _tts_worker_instance and is_functional:
        _tts_worker_instance.submit_talk(texto, on_done_callback)
    elif on_done_callback:
        print("TTS worker indisponível. pulando fala.")
        on_done_callback()