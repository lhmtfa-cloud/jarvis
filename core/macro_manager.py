import json
import os
import pyautogui
from pynput import mouse, keyboard
import time
import utils.vision as vision
import core.command_parser as command_parser

_falar = None
macro_steps = []
last_action_time = None
mouse_listener = None
keyboard_listener = None
pressed_keys = set()
STOP_COMBO = {keyboard.Key.ctrl_l, keyboard.Key.esc}

def inicializar(falar_func):
    global _falar
    _falar = falar_func

def on_click(x, y, button, pressed):
    global macro_steps, last_action_time
    if pressed:
        delay = time.time() - last_action_time if last_action_time else 0
        step = {"action": "click", "x": x, "y": y, "button": str(button).split('.')[-1], "delay": delay}
        macro_steps.append(step); last_action_time = time.time()
        print(f"Gravado: Clique em ({x}, {y})")

def on_press(key):
    global pressed_keys, macro_steps, last_action_time, mouse_listener
    if key in pressed_keys: return
    pressed_keys.add(key)
    if all(k in pressed_keys for k in STOP_COMBO):
        if mouse_listener: mouse_listener.stop()
        return False
    delay = time.time() - last_action_time if last_action_time else 0
    char = f"Key.{key.name}" if not hasattr(key, 'char') else key.char
    step = {"action": "type", "text": char, "delay": delay}
    macro_steps.append(step); last_action_time = time.time()
    print(f"Gravado: Tecla '{char}'")

def on_release(key):
    global pressed_keys
    try:
        if key in pressed_keys:
            pressed_keys.remove(key)
    except KeyError: pass

def carregar_macros():
    if not os.path.exists('macros.json'): return {}
    with open('macros.json', 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except json.JSONDecodeError: return {}

def salvar_macros(macros):
    with open('macros.json', 'w', encoding='utf-8') as f:
        json.dump(macros, f, indent=4)
    print("Arquivo 'macros.json' salvo/atualizado com sucesso!")

def iniciar_gravacao(nome, arquivo=None, sobrescrever=False):
    global macro_steps, last_action_time, mouse_listener, keyboard_listener, pressed_keys
    macros = carregar_macros()
    if nome in macros and not sobrescrever:
        return _falar(f"Essa macro já existe. Diga 'sobrescrever macro {nome}' para substituí-la.")

    if arquivo:
        _falar(f"Abrindo {arquivo} e gravando a macro '{nome}'.")
        try: os.startfile(arquivo); time.sleep(2)
        except Exception: _falar(f"Não consegui abrir {arquivo}.")
    else: _falar(f"Comecei a gravar a macro '{nome}'.")
    
    _falar("Pressione Ctrl e Esc para parar.")
    macro_steps, pressed_keys = [], set(); last_action_time = time.time()
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    mouse_listener.start(); keyboard_listener.start(); keyboard_listener.join()
    _falar("Gravação parada."); macros[nome] = macro_steps; salvar_macros(macros)
    return f"Macro '{nome}' gravada com sucesso."

def criar_macro_visual(comando):
    try:
        partes = comando.replace("aprenda a", "").replace("brenda a", "").split(" clicando em ")
        nome_macro = partes[0].strip()
        nome_imagem = partes[1].strip()
        macros = carregar_macros()
        macros[nome_macro] = [{"action": "click_image", "image_file": nome_imagem, "delay": 0.5}]
        salvar_macros(macros)
        return _falar(f"Ok, aprendi o comando '{nome_macro}'.")
    except Exception:
        return _falar("Não entendi o comando. Use o formato: 'aprenda a [nome] clicando em [imagem]'.")

def processar_comando_basico_adaptado(passo):
    return command_parser.processar_comando_basico(passo, executar=False)

def criar_macro_hibrida(comando):
    partes = comando.replace("aprenda a", "").replace("brenda a", "").split(" pelos passos ")
    nome_nova_macro = partes[0].strip()
    passos_falados = [p.strip() for p in partes[1].split(" e ")]
    macros = carregar_macros()
    nova_macro_steps = []
    
    for passo in passos_falados:
        if passo in macros:
            nova_macro_steps.append({"action": "execute_macro", "macro_name": passo, "delay": 0.5})
            continue
        
        comando_empacotado = processar_comando_basico_adaptado(passo)
        if comando_empacotado:
            comando_empacotado["delay"] = 0.5
            nova_macro_steps.append(comando_empacotado)
            continue
            
        return _falar(f"Não reconheci o passo '{passo}'. Operação cancelada.")
        
    _falar(f"Criando a macro híbrida '{nome_nova_macro}'.")
    macros[nome_nova_macro] = nova_macro_steps
    salvar_macros(macros)
    return f"Macro híbrida '{nome_nova_macro}' criada."

def apagar_macro(comando):
    nome_macro = comando.replace("apagar macro", "").strip()
    macros = carregar_macros()
    if nome_macro in macros:
        del macros[nome_macro]; salvar_macros(macros)
        return _falar(f"Macro '{nome_macro}' apagada.")
    else: return _falar("Não encontrei essa macro para apagar.")

def executar_macro(nome):
    macros = carregar_macros()
    if nome not in macros:
        return None 
        
    pyautogui.FAILSAFE = False
    _falar(f"Executando a macro '{nome}'.")
    for step in macros.get(nome, []):
        time.sleep(step.get("delay", 0))
        action = step.get("action")
        
        if action == "click": pyautogui.click(x=step["x"], y=step["y"], button=step["button"])
        elif action == "type":
            text = step["text"]
            if text.startswith("Key."): pyautogui.press(text.replace("Key.","").lower())
            else: pyautogui.write(text, interval=0.01)
        elif action == "execute_macro": executar_macro(step["macro_name"])
        elif action == "click_image": vision.clicar_na_imagem(step["image_file"])
        elif action == "call_function":
            command_parser.executar_funcao_empacotada(step)

    pyautogui.FAILSAFE = True
    return f"Macro '{nome}' finalizada."

def processar_comando_admin(comando):
    if comando.startswith(("aprenda a", "brenda a")) and "clicando em" in comando:
        return criar_macro_visual(comando)
    if comando.startswith(("aprenda a", "brenda a")) and "pelos passos" in comando:
        return criar_macro_hibrida(comando)
        
    if comando.startswith("sobrescrever macro"):
        comando_real = comando.replace("sobrescrever macro", "aprenda a", 1)
        return processar_comando_admin(comando_real, sobrescrever=True)
        
    if comando.startswith(("aprenda a", "brenda a")):
        macro_name = comando.replace("aprenda a", "").replace("brenda a", "").strip()
        arquivo = None
        if "abrindo o arquivo de nome" in macro_name:
            macro_name, arquivo = [p.strip() for p in macro_name.split(" abrindo o arquivo de nome ")]
        if macro_name:
            return iniciar_gravacao(macro_name, arquivo)
            
    if comando.startswith("apagar macro"):
        return apagar_macro(comando)
        
    return "Comando de admin não reconhecido."