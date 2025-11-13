import os
import subprocess
import platform
from thefuzz import fuzz
from core.vocabulary import FOLDER_ALIASES

def find_folder_path(folder_name: str) -> str:
    """Encontra o caminho completo de uma pasta a partir de um apelido."""
    return FOLDER_ALIASES.get(folder_name.lower())

def find_closest_file_match(target_filename: str, folder_path: str, min_similarity=70) -> str:
    """Encontra o nome de arquivo mais próximo dentro de uma pasta."""
    if not os.path.isdir(folder_path):
        return None
        
    best_match = None
    highest_score = 0
    target_lower = target_filename.lower()
    target_name, target_ext = os.path.splitext(target_lower)

    for filename_in_folder in os.listdir(folder_path):
        if os.path.isdir(os.path.join(folder_path, filename_in_folder)):
            continue
            
        filename_lower = filename_in_folder.lower()
        name_in_folder, ext_in_folder = os.path.splitext(filename_lower)
        
        current_score = 0
        
        if target_ext:
            if ext_in_folder == target_ext:
                if name_in_folder.startswith(target_name):
                    current_score = 90 + (len(target_name) / len(name_in_folder) * 10)
                else:
                    current_score = fuzz.token_set_ratio(target_name, name_in_folder)
        else:
            if name_in_folder.startswith(target_name):
                current_score = 90
            else:
                current_score = fuzz.token_set_ratio(target_name, name_in_folder)

        fallback_score = fuzz.token_set_ratio(target_lower, filename_lower)
        final_score = max(current_score, fallback_score)
        
        if final_score > highest_score:
            highest_score = final_score
            best_match = filename_in_folder
            
    if highest_score >= min_similarity:
        return best_match
    else:
        return None

def open_file(file_path: str) -> str:
    """Abre (executa) um arquivo usando o programa padrão do sistema."""
    if not os.path.exists(file_path):
        print(f"Erro: Caminho não existe '{file_path}'")
        return f"Erro: O caminho '{file_path}' não foi encontrado."
    
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(file_path)
            return f"Abrindo '{os.path.basename(file_path)}'."
        elif system == "Darwin": # macOS
            subprocess.run(['open', file_path])
            return f"Abrindo '{os.path.basename(file_path)}'."
        else: # Linux
            subprocess.run(['xdg-open', file_path])
            return f"Abrindo '{os.path.basename(file_path)}'."
    except Exception as e:
        return f"Erro ao tentar abrir o arquivo: {e}"

def select_file_in_explorer(file_path: str) -> str:
    """Seleciona (mostra) um arquivo no explorador de arquivos do sistema."""
    if not os.path.exists(file_path):
        print(f"Erro: Caminho não existe '{file_path}'")
        return f"Erro: O caminho '{file_path}' não foi encontrado."
        
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(['explorer', '/select,', file_path])
            return f"Arquivo '{os.path.basename(file_path)}' selecionado."
        elif system == "Darwin": # macOS
            subprocess.run(['open', '-R', file_path])
            return f"Arquivo '{os.path.basename(file_path)}' revelado no Finder."
        else: # Linux
            folder = os.path.dirname(file_path)
            subprocess.run(['xdg-open', folder])
            return f"Pasta '{folder}' aberta."
    except Exception as e:
        return f"Erro ao tentar abrir o explorador de arquivos: {e}"