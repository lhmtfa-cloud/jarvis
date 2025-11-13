from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import queue
import webbrowser
import threading
from threading import Timer
import time

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'secret_key_para_assistente'
socketio = SocketIO(app, async_mode='threading')

text_queue = None
command_parser = None
tts_engine = None
audio_listener = None 

def inicializar_gui(q, parser, tts, listener): 
    global text_queue, command_parser, tts_engine, audio_listener
    text_queue = q
    command_parser = parser
    tts_engine = tts
    audio_listener = listener 

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Frontend conectado.')
    emit('new_message', {'sender': 'ASSISTENTE', 'text': 'Conectado. Ouvindo...'})
    emit('status_update', {'text': 'Ouvindo...', 'duration': 0})

@socketio.on('toggle_tts')
def handle_toggle_tts(data):
    if tts_engine:
        tts_engine.set_enabled(data['enabled'])

@socketio.on('toggle_pause')
def handle_toggle_pause(data):
    if audio_listener:
        if data['paused']:
            audio_listener.pause()
            emit('status_update', {'text': 'Pausado', 'duration': 0})
        else:
            audio_listener.resume()
            emit('status_update', {'text': 'Ouvindo...', 'duration': 0})

def background_task_queue():
    while True:
        socketio.sleep(0.1)
        try:
            data = text_queue.get_nowait()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Erro Crítico na Fila: {e}")
            continue

        try:
            if data['type'] == 'status':
                socketio.emit('status_update', data)
                continue
                
            if data['type'] == 'error':
                socketio.emit('new_message', {'sender': 'ERRO', 'text': data['text']})
                socketio.emit('status_update', {'text': 'Ouvindo... (Erro)', 'last_stage': 'Erro', 'duration': 0})
                continue
                
            if data['type'] == 'text':
                texto_falado = data['text']
                
                socketio.emit('status_update', {
                    'text': 'Texto Recebido', 
                    'last_stage': data['last_stage'], 
                    'duration': data['duration']
                })
                socketio.emit('new_message', {'sender': 'VOCÊ', 'text': texto_falado})

                t_start_cmd = time.time()
                socketio.emit('status_update', {'text': 'Processando Comando...', 'duration': 0})
                
                if audio_listener:
                    audio_listener.pause()
                
                try:
                    resultado_comando = command_parser.parse_and_execute(texto_falado)
                    t_end_cmd = time.time()
                    duration = t_end_cmd - t_start_cmd
                    
                    socketio.emit('status_update', {
                        'text': 'Comando Processado', 
                        'last_stage': 'Processamento', 
                        'duration': round(duration, 2)
                    })
                
                except Exception as e:
                    error_msg = f"Erro no loop de background: {e}"
                    print(error_msg)
                    socketio.emit('new_message', {'sender': 'ERRO', 'text': error_msg})
                    resultado_comando = "Ocorreu um erro ao processar o comando."

                socketio.emit('new_message', {'sender': 'ASSISTENTE', 'text': resultado_comando})
                
                
                known_conflict_strings = ["WhatsApp ativado.", "WhatsApp iniciado e ativado."]
                should_speak = True
                if any(s in resultado_comando for s in known_conflict_strings):
                    should_speak = False

                
                if tts_engine and should_speak:
                    t_start_tts = time.time()
                    socketio.emit('status_update', {'text': 'Falando...', 'duration': 0})
                    
                    def on_tts_finished():
                        t_end_tts = time.time()
                        duration = t_end_tts - t_start_tts
                        
                        if audio_listener:
                            audio_listener.resume()
                        
                        socketio.emit('status_update', {
                            'text': 'Ouvindo...', 
                            'last_stage': 'TTS', 
                            'duration': round(duration, 2)
                        })

                    tts_engine.falar(resultado_comando, on_done_callback=on_tts_finished)
                
                else:
                    if audio_listener:
                        audio_listener.resume()
                    socketio.emit('status_update', {'text': 'Ouvindo...', 'last_stage': 'Processamento', 'duration': 0})
                    
        except Exception as e:
            print(f"Erro inesperado no loop principal: {e}")
            if audio_listener:
                audio_listener.resume()

def run_server():
    print("Iniciando servidor web...")
    socketio.start_background_task(target=background_task_queue)
    url = "http://127.0.0.1:5000"
    Timer(1, lambda: webbrowser.open(url)).start()
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)