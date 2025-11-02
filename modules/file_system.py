# modules/file_system.py

import os
import subprocess
import platform
from pathlib import Path
from thefuzz import fuzz

# Mapeia nomes falados para caminhos reais. Pode ser expandido.
FOLDER_ALIASES = {
    "download": str(Path.home() / "Downloads"),
    "downloads": str(Path.home() / "Downloads"),
    "transferências": str(Path.home() / "Downloads"),
    "documentos": str(Path.home() / "Documents"),
    "área de trabalho": str(Path.home() / "Desktop"), # <-- ADICIONE ESTA LINHA
}

def find_folder_path(folder_name: str) -> str:
    """Encontra o caminho completo de uma pasta a partir de um apelido."""
    return FOLDER_ALIASES.get(folder_name.lower())

# O resto do arquivo continua igual...
def find_closest_file_match(target_filename: str, folder_path: str, min_similarity=70) -> str:
    if not os.path.isdir(folder_path):
        return None
    best_match = None
    highest_score = 0
    for filename_in_folder in os.listdir(folder_path):
        score = fuzz.ratio(target_filename.lower(), filename_in_folder.lower())
        if score > highest_score:
            highest_score = score
            best_match = filename_in_folder
    if highest_score >= min_similarity:
        return best_match
    else:
        return None

def open_explorer_and_select(file_path: str):
    if not os.path.exists(file_path):
        print(f"Erro: Caminho não existe '{file_path}'")
        return f"Erro: O caminho '{file_path}' não foi encontrado."
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(['explorer', '/select,', file_path])
            return f"Arquivo '{os.path.basename(file_path)}' selecionado."
        elif system == "Darwin":
            subprocess.run(['open', '-R', file_path])
            return f"Arquivo '{os.path.basename(file_path)}' revelado no Finder."
        else:
            folder = os.path.dirname(file_path)
            subprocess.run(['xdg-open', folder])
            return f"Pasta '{folder}' aberta."
    except Exception as e:
        return f"Erro ao tentar abrir o explorador de arquivos: {e}"