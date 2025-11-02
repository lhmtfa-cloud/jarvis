# main.py

import tkinter as tk
from tkinter import scrolledtext
import queue
import os
import pyaudio

from utils.listener import AudioListener
from core.command_parser import parse_and_execute # <<< IMPORTAMOS O PARSER

# --- CONFIGURAÇÕES (sem alterações) ---
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

# --- VERIFICAÇÃO INICIAL (sem alterações) ---
if not os.path.isdir(LOCAL_MODEL_PATH):
    print(f"ERRO: Pasta do modelo convertido não encontrada em '{LOCAL_MODEL_PATH}'")
    print("Verifique se a pasta existe e se o caminho está correto.")
    exit()

# --- LÓGICA DA APLICAÇÃO ---
text_queue = queue.Queue()
audio_listener = AudioListener(
    model_id_original=ORIGINAL_MODEL_ID,
    model_path_local=LOCAL_MODEL_PATH,
    text_queue=text_queue, 
    config=AUDIO_CONFIG
)

def iniciar_escuta():
    audio_listener.start()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    status_label.config(text="Ouvindo...")

def parar_escuta():
    audio_listener.stop()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    status_label.config(text="Pronto.")

def verificar_fila_gui():
    try:
        texto_falado = text_queue.get_nowait()
        
        # Mostra o que foi ouvido
        memoria_widget.insert(tk.END, f"VOCÊ: {texto_falado}\n", "user_text")

        if "ERRO:" in texto_falado:
            memoria_widget.insert(tk.END, f"{texto_falado}\n\n", "error")
        else:
            # <<< A GRANDE MUDANÇA ESTÁ AQUI >>>
            # Em vez de apenas mostrar o texto, nós o processamos
            resultado_comando = parse_and_execute(texto_falado)
            
            # Mostra a resposta do assistente
            memoria_widget.insert(tk.END, f"ASSISTENTE: {resultado_comando}\n\n", "assistant_text")

        memoria_widget.see(tk.END)
    except queue.Empty:
        pass
    finally:
        app.after(100, verificar_fila_gui)

def ao_fechar():
    parar_escuta()
    app.destroy()

# --- GUI (com pequenas melhorias de estilo) ---
app = tk.Tk()
app.title("Assistente Virtual - Comandos")
app.geometry("700x500")
app.configure(bg="#2b2b2b")

status_label = tk.Label(app, text="Pronto.", font=("Segoe UI", 12), pady=10, bg="#2b2b2b", fg="white")
status_label.pack()

memoria_widget = scrolledtext.ScrolledText(app, wrap=tk.WORD, font=("Consolas", 14), state=tk.NORMAL, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", relief="flat")
memoria_widget.tag_config("error", foreground="#ff6b6b")
memoria_widget.tag_config("user_text", foreground="#7ec699") # Verde para o usuário
memoria_widget.tag_config("assistant_text", foreground="#68a0f9") # Azul para o assistente
memoria_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(app, bg="#2b2b2b")
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Iniciar Escuta", command=iniciar_escuta, font=("Segoe UI", 12), bg="#4CAF50", fg="white", relief="flat", padx=10)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Parar Escuta", command=parar_escuta, font=("Segoe UI", 12), state=tk.DISABLED, bg="#f44336", fg="white", relief="flat", padx=10)
stop_button.pack(side=tk.LEFT, padx=5)

app.protocol("WM_DELETE_WINDOW", ao_fechar)
verificar_fila_gui()
app.mainloop()