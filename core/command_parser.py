# core/command_parser.py

from utils import text_processor
from modules import file_system
from modules import whatsapp_automator 
import os

def parse_and_execute(transcribed_text: str) -> str:
    """
    Analisa o texto transcrito, identifica o comando e o executa.
    Retorna uma string com o resultado da operação para a GUI.
    """
    # --- LÓGICA DO WHATSAPP (Adicionamos antes da lógica de arquivos) ---
    if "whatsapp" in transcribed_text or "zap" in transcribed_text or "avise" in transcribed_text:
        contact, message = text_processor.extract_whatsapp_command(transcribed_text)
        if contact and message:
            return whatsapp_automator.send_message_to_contact(contact, message)

    # --- LÓGICA DE MANIPULAÇÃO DE ARQUIVOS (existente) ---
    folder_name, file_name = text_processor.extract_file_command_parts(transcribed_text)
    if folder_name and file_name:
        path = file_system.find_folder_path(folder_name)
        if not path:
            return f"Não conheço a pasta '{folder_name}'. Verifique os apelidos definidos."
        
        best_match_filename = file_system.find_closest_file_match(file_name, path)
        if not best_match_filename:
            return f"Não encontrei nada parecido com '{file_name}' na pasta '{folder_name}'."
        
        full_path = os.path.join(path, best_match_filename)
        result = file_system.open_explorer_and_select(full_path)
        return result
        
    return "Comando não reconhecido."