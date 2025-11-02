from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import queue
import webbrowser
from threading import Timer

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

@socketio.on('toggle_tts')
def handle_toggle_tts(data):
    if tts_engine:
        tts_engine.set_enabled(data['enabled'])

@socketio.on('toggle_pause')
def handle_toggle_pause(data):
    if audio_listener:
        if data['paused']:
            audio_listener.pause()
            emit('status_update', {'text': 'Pausado'})
        else:
            audio_listener.resume()
            emit('status_update', {'text': 'Ouvindo...'})

def background_task_queue():
    while True:
        socketio.sleep(0.1)
        try:
            texto_falado = text_queue.get_nowait()
            socketio.emit('new_message', {'sender': 'VOCÊ', 'text': texto_falado})
            
            if "ERRO:" in texto_falado:
                socketio.emit('new_message', {'sender': 'ERRO', 'text': texto_falado})
            else:
                resultado_comando = command_parser.parse_and_execute(texto_falado)
                socketio.emit('new_message', {'sender': 'ASSISTENTE', 'text': resultado_comando})
                if tts_engine:
                    tts_engine.falar(resultado_comando)
                    
        except queue.Empty:
            continue
        except Exception as e:
            error_msg = f"Erro no loop de background: {e}"
            print(error_msg)
            socketio.emit('new_message', {'sender': 'ERRO', 'text': error_msg})

def run_server():
    print("Iniciando servidor web...")
    socketio.start_background_task(target=background_task_queue)
    url = "http://127.0.0.1:5000"
    Timer(1, lambda: webbrowser.open(url)).start()
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)