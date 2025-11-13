import os
from pathlib import Path

# --- Dicionário de Pastas (de file_system.py) ---
FOLDER_ALIASES = {
    "download": str(Path.home() / "Downloads"),
    "downloads": str(Path.home() / "Downloads"),
    "transferência": str(Path.home() / "Downloads"),
    "transferências": str(Path.home() / "Downloads"),
    "documento": str(Path.home() / "Documents"),
    "documentos": str(Path.home() / "Documents"),
    "área de trabalho": str(Path.home() / "Desktop"),
}

# --- Dicionários de Palavras-chave (de text_processor.py) ---
ACTION_KEYWORDS_OPEN = ["abrir", "abra", "executar", "execute", "tocar", "toque", "cabra", "cabro", "sabro"]
ACTION_KEYWORDS_SELECT = ["selecionar", "selecione", "mostrar", "mostre", "localizar", "localize", "onde está", "achar", "ache"]
LOCATION_KEYWORDS = ["em", "na", "de", "da", "no"]
FILE_KEYWORDS = ["o arquivo", "arquivo"]

# --- Dicionário de Números (de text_processor.py) ---
NUMBER_WORDS = {
    'zero': '0', 'um': '1', 'dois': '2', 'três': '3',
    'quatro': '4', 'cinco': '5', 'seis': '6', 'sete': '7',
    'oito': '8', 'nove': '9', 'dez': '10', 'onze': '11',
    'doze': '12', 'treze': '13', 'catorze': '14', 'quinze': '15',
    'dezesseis': '16', 'dezessete': '17', 'dezoito': '18',
    'dezenove': '19', 'vinte': '20'
}