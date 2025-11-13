import re
from typing import Tuple
from core.vocabulary import (
    FOLDER_ALIASES, 
    ACTION_KEYWORDS_OPEN, 
    ACTION_KEYWORDS_SELECT, 
    LOCATION_KEYWORDS, 
    FILE_KEYWORDS, 
    NUMBER_WORDS
)

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    
    text = text.replace(" ponto ", ".")
    
    text = re.sub(r'[,\?!\'"]', '', text)
    text = re.sub(r'\.$', '', text)
    
    for _ in range(3):
        for word, digit in NUMBER_WORDS.items():
            text = text.replace(f" {word} ", f" {digit} ")
            text = text.replace(f" {word}.", f" {digit}.")
    
    text = re.sub(r'(\d) (\d)', r'\1\2', text)
    
    text = text.replace('-', ' ')
    
    return text.strip()

def extract_file_command_parts(text: str) -> Tuple[str, str, str]:
    
    text_normalized = normalize_text(text)
    
    found_folder, file_name, action = None, None, None

    if any(word in text_normalized for word in ACTION_KEYWORDS_OPEN):
        action = "open"
    elif any(word in text_normalized for word in ACTION_KEYWORDS_SELECT):
        action = "select"

    sorted_aliases = sorted(FOLDER_ALIASES.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if alias in text_normalized:
            found_folder = alias 
            break
    
    if not found_folder:
        return None, None, None 

    match = re.search(r'([\w\d\s-]+\.[\w\d]+)', text_normalized) 
    
    all_keywords = ACTION_KEYWORDS_OPEN + ACTION_KEYWORDS_SELECT + LOCATION_KEYWORDS + FILE_KEYWORDS
    
    if match:
        file_name = match.group(1).strip()
        for keyword in all_keywords:
            file_name = file_name.replace(keyword, "")
        file_name = file_name.strip()
    else:
        file_name = text_normalized.replace(found_folder, "")
        for keyword in all_keywords:
            file_name = file_name.replace(keyword, "")
        file_name = file_name.strip()
    
    if not file_name: 
        return None, None, None
        
    if not action:
        action = "open"
        
    return action, found_folder, file_name

def extract_whatsapp_command(text: str) -> Tuple[str, str]:
    match = re.search(r'(avise|mande|envie) (.*?) (que|para|dizendo que) (.*)', text)
    
    if match:
        contact = match.group(2).strip()
        message = match.group(4).strip()
        
        contact = contact.replace("para o ", "").replace("para a ", "").strip()
        
        if contact and message:
            return contact, message
            
    return None, None