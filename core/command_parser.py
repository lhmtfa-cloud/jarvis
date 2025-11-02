import time
import os
from utils import text_processor, vision
from modules import file_system
from modules import whatsapp_automator
import core.macro_manager as macro_manager

is_admin_mode = False
last_admin_time = 0

COMANDOS_BASICOS_VISAO = {
    "copiar de": vision.copiar_texto_delimitado,
    "selecionar de": vision.selecionar_texto_delimitado,
    "copiar o texto da imagem": vision.copiar_texto_da_imagem,
    "clicar na imagem": vision.clicar_na_imagem,
    "clicar": vision.clicar_na_imagem,
    "digite": vision.digitar_em_caixa_generica,
    "criar arquivo de texto": vision.criar_arquivo_txt,
    "compare": vision.comparar_valores,
    "some": vision.calcular_valores,
    "subtraia": vision.calcular_valores,
    "multiplique": vision.calcular_valores,
    "dividido por": vision.calcular_valores,
    "colar": vision.colar_texto,
    "espere": vision.esperar,
    "copiar seleção": vision.copiar_selecao,
}

def executar_funcao_empacotada(step):
    funcao = COMANDOS_BASICOS_VISAO.get(step["function_keyword"])
    if funcao: 
        funcao(*step["args"])
    else: 
        print(f"Função desconhecida na macro: {step['function_keyword']}")

def processar_comando_basico(comando, executar=True):
    for keyword, funcao in COMANDOS_BASICOS_VISAO.items():
        if comando.startswith(keyword):
            argumentos_str = comando.replace(keyword, "", 1).strip()
            args = []

            if keyword in ["copiar de", "selecionar de"]:
                partes = argumentos_str.split(" até ")
                if len(partes) == 2: args = [partes[0].strip(), partes[1].strip()]
                else: return None
            
            elif keyword in ["digite", "clicar na imagem", "clicar", "espere", "copiar o texto da imagem"]:
                args = [argumentos_str]
            
            elif keyword == "colar":
                args = []

            elif keyword == "criar arquivo de texto":
                partes = argumentos_str.replace("com nome", "").split(" e conteúdo ")
                if len(partes) == 2: args = [partes[0].strip(), partes[1].strip()]
                else: return None

            elif keyword in ["compare", "some", "subtraia", "multiplique", "dividido por"]:
                partes = argumentos_str.split()
                op_str = " ".join(partes[1:-1]) if len(partes) > 2 else keyword
                args = [partes[0], op_str, partes[-1]]
            
            if executar:
                try:
                    funcao(*args)
                    return "Comando de visão executado."
                except Exception as e:
                    print(f"Erro no parser ao executar {funcao.__name__}: {e}")
                    return "Ocorreu um erro ao executar o comando de visão."
            else:
                return {"action": "call_function", "function_keyword": keyword, "args": args}
            
    return None

def parse_and_execute(transcribed_text: str) -> str:
    global is_admin_mode, last_admin_time
    
    if is_admin_mode and (time.time() - last_admin_time > 300):
        is_admin_mode = False
        return "Saindo do modo admin por inatividade."

    if any(s in transcribed_text for s in ["modo número 0012"]):
        is_admin_mode = True
        last_admin_time = time.time()
        return "Modo administrador ativado."

    if any(s in transcribed_text for s in ["sair do modo admin"]):
        is_admin_mode = False
        return "Modo administrador desativado."

    if is_admin_mode and any(transcribed_text.startswith(s) for s in ["aprenda a", "brenda a", "apagar macro", "sobrescrever macro"]):
        last_admin_time = time.time()
        return macro_manager.processar_comando_admin(transcribed_text)
    
    if "whatsapp" in transcribed_text or "zap" in transcribed_text or "avise" in transcribed_text:
        contact, message = text_processor.extract_whatsapp_command(transcribed_text)
        if contact and message:
            return whatsapp_automator.send_message_to_contact(contact, message)

    folder_name, file_name = text_processor.extract_file_command_parts(transcribed_text)
    if folder_name and file_name:
        path = file_system.find_folder_path(folder_name)
        if not path:
            return f"Não conheço a pasta '{folder_name}'."
        best_match_filename = file_system.find_closest_file_match(file_name, path)
        if not best_match_filename:
            return f"Não encontrei nada parecido com '{file_name}' na pasta '{folder_name}'."
        full_path = os.path.join(path, best_match_filename)
        return file_system.open_explorer_and_select(full_path)
    
    resultado_basico = processar_comando_basico(transcribed_text, executar=True)
    if resultado_basico:
        return resultado_basico

    resultado_macro = macro_manager.executar_macro(transcribed_text)
    if resultado_macro:
        return resultado_macro
        
    return "Comando não reconhecido."