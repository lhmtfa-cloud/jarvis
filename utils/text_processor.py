import re
from typing import Tuple
from modules.file_system import FOLDER_ALIASES

def normalize_text(text: str) -> str:
    return text.lower().strip().replace('.', '', 1).replace(',', '').replace('-', ' ')

def extract_file_command_parts(text: str) -> Tuple[str, str]:
    text = normalize_text(text)
    found_folder, file_name = None, None
    for alias in FOLDER_ALIASES.keys():
        if alias in text:
            found_folder = alias
            parts = text.split(alias, 1)
            if len(parts) > 1:
                potential_file_name = parts[1].strip()
                match = re.search(r'([\w\d\s-]+\.[\w\d]+)', potential_file_name)
                if match:
                    file_name = match.group(1).strip()
                else:
                    file_name = potential_file_name
            break
    return found_folder, file_name

def extract_whatsapp_command(text: str) -> Tuple[str, str]:
    text = normalize_text(text)
    
    match = re.search(r'^(?:avise|mande|envie|fale para|whatsapp|zap)\s+([a-zA-Z\s]+?)\s+(?:que\s+)?(.*)', text)
    
    if match:
        contact_name = match.group(1).strip()
        message = match.group(2).strip()

        if not message:
            return None, None
        contact_name = re.sub(r'^(o|a|meu|minha)\s+', '', contact_name, flags=re.IGNORECASE).strip()
        contact_name = contact_name.title()
             
        return contact_name, message
        
    return None, None