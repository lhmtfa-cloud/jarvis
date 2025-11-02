import queue
import os
import pyaudio
from utils.listener import AudioListener
import core.command_parser as command_parser
import utils.tts_engine as tts_engine
import utils.gui as gui
import utils.vision as vision
import core.macro_manager as macro_manager

ORIGINAL_MODEL_ID = "pierreguillou/whisper-medium-portuguese"
LOCAL_MODEL_PATH = "./whisper-medium-pt-ct2"
AUDIO_CONFIG = {
    "CHUNK_SIZE": 1024,
    "FORMAT": pyaudio.paInt16,
    "CHANNELS": 1,
    "RATE": 16000,
    "SILENCE_THRESHOLD": 600,
    "SILENCE_DURATION": 1.5,
}

if not os.path.isdir(LOCAL_MODEL_PATH):
    print(f"ERRO: Pasta do modelo convertido não encontrada em '{LOCAL_MODEL_PATH}'")
    print("Execute o script de conversão do modelo CTranslate2 primeiro.")
    exit()

if __name__ == "__main__":
    text_queue = queue.Queue()

    audio_listener = AudioListener(
        model_id_original=ORIGINAL_MODEL_ID,
        model_path_local=LOCAL_MODEL_PATH,
        text_queue=text_queue,
        config=AUDIO_CONFIG,
        compute_type="float32",
        beam_size=3
    )

    print("Iniciando o listener de áudio...")
    audio_listener.start()

    falar_func = tts_engine.falar
    vision.inicializar(falar_func)
    macro_manager.inicializar(falar_func)

    gui.inicializar_gui(
        q=text_queue,
        parser=command_parser,
        tts=tts_engine,
        listener=audio_listener
    )
    
    gui.run_server()