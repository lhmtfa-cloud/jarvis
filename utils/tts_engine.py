import pyttsx3

try:
    engine = pyttsx3.init()
    is_enabled = True
except Exception as e:
    print(f"Erro ao inicializar TTS: {e}")
    engine = None
    is_enabled = False

def set_enabled(status: bool):
    global is_enabled
    is_enabled = status

def falar(texto: str):
    if is_enabled and engine:
        try:
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"Erro no TTS ao falar: {e}")